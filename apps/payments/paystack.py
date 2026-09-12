import hashlib
import hmac
import json
import logging
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger("payments.paystack")


class PaystackService:
    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = getattr(settings, "PAYSTACK_SECRET_KEY", "")
        self.public_key = getattr(settings, "PAYSTACK_PUBLIC_KEY", "")
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    @property
    def is_configured(self):
        return bool(self.secret_key and self.public_key)

    def _request(self, method, endpoint, data=None):
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, json=data, timeout=30
            )
            result = response.json()
            logger.info(f"Paystack {method} {endpoint} -> {response.status_code}")
            return result
        except requests.exceptions.ConnectionError:
            logger.error(f"Paystack connection error: {endpoint}")
            return {"status": False, "message": "Network error. Please check your connection."}
        except requests.exceptions.Timeout:
            logger.error(f"Paystack timeout: {endpoint}")
            return {"status": False, "message": "Request timed out. Please try again."}
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack request error: {endpoint} - {e}")
            return {"status": False, "message": "Payment service error. Please try again."}
        except ValueError:
            logger.error(f"Paystack invalid response: {endpoint}")
            return {"status": False, "message": "Invalid response from payment service."}

    def initialize_transaction(self, email, amount, reference, callback_url=None, metadata=None):
        """Initialize a Paystack transaction."""
        if not self.is_configured:
            logger.warning("Paystack keys not configured")
            return {"status": False, "message": "Payment system not configured. Please contact support."}

        try:
            amount_int = int(Decimal(str(amount)) * 100)
        except (TypeError, ValueError) as e:
            logger.error(f"Invalid amount: {amount} - {e}")
            return {"status": False, "message": "Invalid payment amount."}

        data = {
            "email": email,
            "amount": amount_int,
            "reference": reference,
            "currency": "NGN",
        }
        if callback_url:
            data["callback_url"] = callback_url
        if metadata:
            data["metadata"] = metadata

        return self._request("POST", "/transaction/initialize", data)

    def verify_transaction(self, reference):
        """Verify a transaction by reference."""
        return self._request("GET", f"/transaction/verify/{reference}")

    def get_transaction(self, reference):
        """Get transaction details."""
        return self._request("GET", f"/transaction/{reference}")

    def create_customer(self, email, first_name="", last_name="", phone=""):
        """Create a Paystack customer."""
        data = {"email": email}
        if first_name:
            data["first_name"] = first_name
        if last_name:
            data["last_name"] = last_name
        if phone:
            data["phone"] = phone
        return self._request("POST", "/customer", data)

    def create_plan(self, name, amount, interval="monthly"):
        """Create a payment plan."""
        try:
            amount_int = int(Decimal(str(amount)) * 100)
        except (TypeError, ValueError):
            amount_int = 0
        data = {
            "name": name,
            "amount": amount_int,
            "interval": interval,
            "currency": "NGN",
        }
        return self._request("POST", "/plan", data)

    @staticmethod
    def verify_webhook_signature(signature, payload, secret):
        """Verify Paystack webhook signature."""
        hash_obj = hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha512,
        )
        return hmac.compare_digest(hash_obj.hexdigest(), signature)
