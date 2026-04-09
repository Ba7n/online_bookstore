"""
Management command to create an admin user in Firestore.
Usage: python manage.py create_admin --email admin@example.com --username admin --password password123
"""

import hashlib
from datetime import datetime, timezone
from django.core.management.base import BaseCommand
from firebase_config.firebase import db, Collections


class Command(BaseCommand):
    help = "Create an admin user in Firestore"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Admin email address'
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Admin username'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Admin password'
        )
        parser.add_argument(
            '--phone',
            type=str,
            default='',
            help='Admin phone number (optional)'
        )

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']
        phone = options.get('phone', '')

        # Check if user already exists
        existing = db.collection(Collections.USERS).where('email', '==', email).get()
        if existing:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists!')
            )
            return

        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Create admin user
        try:
            import uuid
            user_id = str(uuid.uuid4())
            
            user_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'password': hashed_password,
                'phone': phone,
                'is_admin': True,
                'profile_image': '',
                'created_at': datetime.now(timezone.utc).isoformat(),
            }

            db.collection(Collections.USERS).document(user_id).set(user_data)

            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Admin user created successfully!\n'
                    f'  User ID: {user_id}\n'
                    f'  Email: {email}\n'
                    f'  Username: {username}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {str(e)}')
            )
