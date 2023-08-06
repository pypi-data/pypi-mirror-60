from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from zonesmart.users.phone_verification.actions import TwilioVerification
from zonesmart.users.tasks import send_verification_code

User = get_user_model()


class UserPhoneUpdateView(APIView):
    def post(self, request: Request, *args, **kwargs):
        phone = request.data.get("phone")
        # Validate if phone number exists in the request body
        if phone is None:
            raise ValidationError({"phone": "Phone number is required."})
        else:
            if phone == self.request.user.phone:
                return Response("New phone matches current.")
        send_verification_code.delay(self.request.user.id, phone)
        return Response("Verification code was sent successfully.")


user_phone_update_view = UserPhoneUpdateView.as_view()


class UserPhoneVerifyView(APIView):
    def post(self, request: Request, *args, **kwargs):
        code = request.data.get("code")
        if code is None:
            raise ValidationError({"code": "Verification code is required."})
        # Get code from cache
        cache_key = f"user_phone_verification_{self.request.user.id}"
        data = cache.get(cache_key)
        if data is None:
            return Response("Nothing to confirm.")
        else:
            verification = TwilioVerification(phone=data["phone"])
            valid = verification.get_verification_status(code=code)
            if not valid:
                raise ValidationError(
                    {
                        "code": "Code is not valid. Try again or resend verification code."
                    }
                )
            else:
                self.request.user.phone = data["phone"]
                self.request.user.save()
                return Response(
                    "Code is valid. Phone number successfully added to the user."
                )


user_phone_verify_view = UserPhoneVerifyView.as_view()
