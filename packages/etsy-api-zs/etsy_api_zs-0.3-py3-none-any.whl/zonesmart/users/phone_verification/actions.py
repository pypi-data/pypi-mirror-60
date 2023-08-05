from django.conf import settings

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


class TwilioVerification:
    def __init__(self, phone):
        self.service_sid = settings.TWILIO_SERVICE_SID
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.channel = settings.TWILIO_CHANNEL
        self.locale = settings.TWILIO_LOCALE
        self.phone = phone
        self.client = self.get_client()

    def get_client(self):
        client = Client(self.account_sid, self.auth_token)
        return client.verify.services(self.service_sid)

    def create_rate_limits(self, unique_name="user_phone", limit=3, interval=60):
        try:
            rate_limits_sid = self.client.rate_limits.create(
                description="Ограничение запросов на верификацию телефона",
                unique_name=unique_name,
            ).sid

            self.client.rate_limits(rate_limits_sid).buckets.create(
                max=limit, interval=interval,
            )
        except TwilioRestException as exception:
            if exception.code in [60208, 60211]:
                pass
            else:
                raise exception

        return {unique_name: self.phone}

    def create_verification_code(self, locale=None, use_rate_limits=True):
        if not locale:
            locale = self.locale

        # if use_rate_limits:
        #     rate_limits = self.get_rate_limits()

        results = self.client.verifications.create(
            to=self.phone,
            channel=self.channel,
            # rate_limits=rate_limits,
            locale=locale,
        )
        return results.sid

    def get_verification_status(self, code) -> bool:
        results = self.client.verification_checks.create(to=self.phone, code=code,)
        return results.valid
