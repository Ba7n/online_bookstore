import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from django.core.management.base import BaseCommand

from firebase_config.firebase import db, Collections


class Command(BaseCommand):
    help = "Update product images using Open Library (with retry + fallback)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting image अपडेट...")

        # 🔁 Setup session with retry strategy
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        products = db.collection(Collections.PRODUCTS).get()

        for product in products:
            data = product.to_dict()

            name = data.get("name")
            author = data.get("author")
            image = data.get("image")

            # Skip if already has image
            if image:
                continue

            if not name:
                continue

            try:
                # ⏳ Prevent rate limiting
                time.sleep(1)

                # 🔍 Search Open Library (title + author)
                url = f"https://openlibrary.org/search.json?title={name}"

                if author:
                    url += f"&author={author}"

                res = session.get(url, timeout=20).json()

                docs = res.get("docs", [])
                if not docs:
                    self.stdout.write(f"No match: {name}")
                    continue

                doc = docs[0]

                # 🖼 Try cover image
                cover_id = doc.get("cover_i")

                if cover_id:
                    image_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                else:
                    image_url = None

                # 🛑 Fallback image (VERY IMPORTANT)
                if not image_url:
                    image_url = "https://via.placeholder.com/300x450?text=No+Image"

                # 💾 Update Firestore
                db.collection(Collections.PRODUCTS).document(product.id).update({
                    "image": image_url
                })

                self.stdout.write(f"Updated: {name}")

            except requests.exceptions.Timeout:
                self.stdout.write(f"Timeout: {name}")

            except requests.exceptions.RequestException as e:
                self.stdout.write(f"Request error: {name} -> {e}")

            except Exception as e:
                self.stdout.write(f"Unexpected error: {name} -> {e}")

        self.stdout.write("✅ Image update completed")