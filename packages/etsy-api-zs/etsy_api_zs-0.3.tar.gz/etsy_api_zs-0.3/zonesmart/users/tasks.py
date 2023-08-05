from uuid import uuid4

from django.core.cache import cache

from config import celery_app

from zonesmart.users.phone_verification.actions import TwilioVerification


@celery_app.task()
def send_verification_code(user_id: uuid4, phone: str):
    verification = TwilioVerification(phone=phone)
    cache_key = f"user_phone_verification_{user_id}"
    sid = verification.create_verification_code()
    data = {"phone": phone, "sid": sid}
    cache.set(cache_key, data)
