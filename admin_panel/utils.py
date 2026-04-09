"""
admin_panel/utils.py
════════════════════
Utility functions for the admin panel.
Handles data conversion, validation, and formatting.
"""

from decimal import Decimal
from typing import Any, Dict, List, Union


def convert_decimal_to_float(data: Any) -> Any:
    """
    Recursively convert all Decimal values to float in data structures.
    
    Firestore cannot serialize Python Decimal objects directly.
    This function recursively processes:
    - Dict values
    - List items
    - Nested structures
    
    Args:
        data: Any Python object (dict, list, Decimal, etc.)
    
    Returns:
        The same data structure with all Decimals converted to float.
    
    Examples:
        >>> convert_decimal_to_float(Decimal('10.50'))
        10.5
        
        >>> convert_decimal_to_float({'price': Decimal('10.50'), 'qty': 2})
        {'price': 10.5, 'qty': 2}
        
        >>> convert_decimal_to_float([Decimal('10.50'), {'price': Decimal('5.50')}])
        [10.5, {'price': 5.5}]
    """
    if isinstance(data, Decimal):
        return float(data)
    
    if isinstance(data, dict):
        return {key: convert_decimal_to_float(value) for key, value in data.items()}
    
    if isinstance(data, (list, tuple)):
        converted = [convert_decimal_to_float(item) for item in data]
        return converted if isinstance(data, list) else tuple(converted)
    
    return data


def calculate_subtotal(quantity: Union[int, float], price: Union[int, float, Decimal]) -> float:
    """
    Calculate subtotal as quantity * price and return as float.
    
    Args:
        quantity: Item quantity (int or float)
        price: Unit price (int, float, or Decimal)
    
    Returns:
        Subtotal as float (always safe for Firestore)
    
    Examples:
        >>> calculate_subtotal(2, Decimal('10.50'))
        21.0
        
        >>> calculate_subtotal(3, 15.50)
        46.5
    """
    try:
        qty = float(quantity)
        prc = float(price) if not isinstance(price, Decimal) else float(price)
        return qty * prc
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid quantity or price: {str(e)}")


def ensure_float_fields(data: Dict, float_fields: List[str]) -> Dict:
    """
    Ensure specific fields in a dict are floats (not Decimal).
    
    Args:
        data: Dictionary to process
        float_fields: List of field names to convert to float
    
    Returns:
        Modified dictionary with float-converted fields
    
    Example:
        >>> data = {'price': Decimal('10.50'), 'tax': Decimal('1.50')}
        >>> ensure_float_fields(data, ['price', 'tax'])
        {'price': 10.5, 'tax': 1.5}
    """
    for field in float_fields:
        if field in data and isinstance(data[field], Decimal):
            data[field] = float(data[field])
    return data


def sanitize_for_firestore(data: Dict) -> Dict:
    """
    Sanitize data dictionary for Firestore storage.
    
    Removes or converts problematic types:
    - Converts Decimal to float
    - Handles None values
    - Validates basic structure
    
    Args:
        data: Dictionary to sanitize
    
    Returns:
        Sanitized dictionary safe for Firestore
    
    Example:
        >>> data = {'price': Decimal('10.50'), 'name': 'Book', 'notes': None}
        >>> sanitize_for_firestore(data)
        {'price': 10.5, 'name': 'Book'}
    """
    sanitized = {}
    for key, value in data.items():
        # Skip None values
        if value is None:
            continue
        
        # Convert Decimals
        if isinstance(value, Decimal):
            sanitized[key] = float(value)
        # Recursively process nested dicts
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_firestore(value)
        # Process lists
        elif isinstance(value, list):
            sanitized[key] = [
                convert_decimal_to_float(item) if isinstance(item, Decimal)
                else sanitize_for_firestore(item) if isinstance(item, dict)
                else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def normalize_payment_status(db_status: str) -> str:
    """
    Normalize database payment status to UI-friendly status.
    
    Database stores: "Paid", "Failed", "Pending", "Refunded"
    UI displays: "success", "failed", "pending", "refunded"
    
    Args:
        db_status: Payment status from database
    
    Returns:
        Normalized status for UI display
    
    Examples:
        >>> normalize_payment_status("Paid")
        "success"
        
        >>> normalize_payment_status("Failed")
        "failed"
        
        >>> normalize_payment_status(None)
        "pending"
    """
    if not db_status:
        return "pending"
    
    status_map = {
        "Paid": "success",
        "paid": "success",
        "SUCCESS": "success",
        "Success": "success",
        "Failed": "failed",
        "failed": "failed",
        "FAILED": "failed",
        "Pending": "pending",
        "pending": "pending",
        "PENDING": "pending",
        "Refunded": "refunded",
        "refunded": "refunded",
        "REFUNDED": "refunded",
    }
    
    return status_map.get(str(db_status).strip(), "pending")


def denormalize_payment_status(ui_status: str) -> str:
    """
    Convert UI status filter back to database status.
    
    UI sends: "success", "failed"
    Database expects: "Paid", "Failed"
    
    Args:
        ui_status: Status filter from UI
    
    Returns:
        Database status for querying
    
    Examples:
        >>> denormalize_payment_status("success")
        "Paid"
        
        >>> denormalize_payment_status("failed")
        "Failed"
    """
    if not ui_status:
        return ""
    
    status_map = {
        "success": "Paid",
        "failed": "Failed",
        "pending": "Pending",
        "refunded": "Refunded",
    }
    
    return status_map.get(str(ui_status).strip().lower(), "")


def get_transaction_id(payment_data: Dict) -> str:
    """
    Safely extract transaction ID from payment data.
    
    Handles both old and new field names:
    - razorpay_payment_id (preferred)
    - transaction_id (fallback)
    - razorpay_transaction_id (legacy)
    
    Args:
        payment_data: Payment dictionary from database
    
    Returns:
        Transaction ID or "N/A" if not found
    
    Examples:
        >>> data = {"razorpay_payment_id": "pay_123"}
        >>> get_transaction_id(data)
        "pay_123"
        
        >>> data = {}
        >>> get_transaction_id(data)
        "N/A"
    """
    if not payment_data:
        return "N/A"
    
    # Try primary field
    transaction_id = payment_data.get('razorpay_payment_id')
    if transaction_id:
        return str(transaction_id).strip()
    
    # Try fallback fields
    transaction_id = payment_data.get('transaction_id')
    if transaction_id:
        return str(transaction_id).strip()
    
    transaction_id = payment_data.get('razorpay_transaction_id')
    if transaction_id:
        return str(transaction_id).strip()
    
    return "N/A"
