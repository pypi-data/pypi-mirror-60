from django.views.decorators.csrf import csrf_exempt

import xmltodict
from rest_framework import status
from rest_framework.parsers import BaseParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from zonesmart.utils.logger import get_logger

logger = get_logger(app_name=__name__)


def validate_signature(signature):
    pass


class ParserException(Exception):
    pass


class NotificationParser(BaseParser):
    media_type = "text/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        try:
            data = dict(xmltodict.parse(stream))
        except (ParserException, xmltodict.ParsingInterrupted) as exc:
            logger.info(f"XML parse error - {str(exc)}")
            data = None

        return data


class ProcessNotificationAPIVIew(APIView):
    permission_classes = [AllowAny]
    parser_classes = [NotificationParser]

    def post(self, request: Request, *args, **kwargs):
        # marketplace_user_account_id = request.query_params.get(
        #     "marketplace_user_account_id"
        # )
        try:
            envelope = request.data["soapenv:Envelope"]
            # header = envelope["soapenv:Header"]
            body = envelope["soapenv:Body"]
            data = body[next(iter(body))]
            notification_type = data["NotificationEventName"]
            # TODO: Validate signature
            # signature = header["ebl:RequesterCredentials"]["ebl:NotificationSignature"]["#text"]
            # logger.info(f"signature: {signature}")
            # Calc md5 hash
            # ebay_time = str(datetime.now())
            # dev_id = "087611bd-15a3-4fed-8c2b-5e112fc54e30"
            # app_id = "Zonesmar-testapp-PRD-e447bf109-5c790707"
            # cert_id = "PRD-447bf10916b1-f18a-4e3d-9a77-37f4"
            # hash = hashlib.md5(dev_id.encode())
            # print(hash.digest().decode().encode("base64").strip())
            # TODO: Do action depends on notification type
            logger.info(f"notification_type: {notification_type}")
        except Exception as e:
            logger.info(f"notification view exception: {str(e)}")
        finally:
            return Response(status=status.HTTP_200_OK)


process_notification_api_view = csrf_exempt(ProcessNotificationAPIVIew.as_view())
