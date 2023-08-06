import datetime

from django.db.models import QuerySet

from ebay.api.ebay_trading_api_action import EbayTradingAPIAction
from ebay.negotiation.serializers.message import DownloadEbayMessageSerializer


class GetEbayMessageList(EbayTradingAPIAction):
    """
    GetMyMessages:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/GetMyMessages.html
    """

    verb = "GetMyMessages"

    folder_id_to_name = {
        0: "Inbox",
        1: "Sent",
        2: "Trash",
        3: "Archive",
    }

    def get_params(
        self,
        detail_level="ReturnHeaders",
        folder_id: int = None,
        message_ids: list = [],
        days_ago: int = 30,
        **kwargs,
    ):
        if message_ids:
            if detail_level == "ReturnMessages":
                assert (
                    len(message_ids) <= 10
                ), 'Размер "message_ids" не должен превышать 10.'
            folder_id = None
            days_ago = None

        if days_ago:
            assert 0 <= days_ago <= 90, "0 <= days_ago <= 90"
            EndTime = datetime.datetime.now()
            StartTime = EndTime - datetime.timedelta(days=days_ago)
        else:
            StartTime = None
            EndTime = None

        return {
            "DetailLevel": detail_level,
            "FolderID": folder_id,
            "MessageIDs": {"MessageID": message_ids},
            "EndTime": EndTime,
            "StartTime": StartTime,
        }

    def success_trigger(self, message, objects, **kwargs):
        if objects["data"].get("FolderID", None):
            objects["results"]["Folder name"] = self.folder_id_to_name[
                int(objects["data"]["FolderID"])
            ]

        if objects["data"]["DetailLevel"] == "ReturnSummary":
            results = objects["results"]["Summary"]
        else:
            results = objects["results"]["Messages"]
            if results:
                results = results.get("Message", [])
                if not isinstance(results, list):
                    results = [results]
            else:
                results = []

        objects["results"] = results

        return super().success_trigger(message, objects, **kwargs)


class RemoteDownloadEbayMessageList(GetEbayMessageList):
    FIELD_MAPPING = [
        ("message_id", "MessageID"),
        ("sender", "Sender"),
        ("sender_id", "SendingUserID"),
        ("recipient_id", "RecipientUserID"),
        ("recipient", "SendToName"),
        ("subject", "Subject"),
        ("read", "Read"),
        ("receive_date", "ReceiveDate"),
        ("expiration_date", "ExpirationDate"),
        ("message_type", "MessageType"),
        ("replied", "Replied"),
    ]
    MESSAGES_CHUNK = 10

    def parse_message_data(self, data: dict):
        """
        Parses eBay's data fields to local field names.
        """
        parsed_data = dict()
        # Parse incoming data to local
        for field_mapping in self.FIELD_MAPPING:
            local_name, received_name = field_mapping
            if received_name in data:  # protect for non None values in the parsed_data
                parsed_data[local_name] = data[received_name]
        # Custom parse for content
        parsed_data["content"] = data["Content"] if "Content" in data else data["Text"]
        # Custom parse for nested Folder
        folder_data = data.get("Folder")
        if folder_data:
            parsed_data["folder_id"] = folder_data["FolderID"]
        # Custom parse for nested ResponseDetails
        response_details = data.get("ResponseDetails")
        if response_details:
            parsed_data["response_enabled"] = response_details.get("ResponseEnabled")
            parsed_data["response_url"] = response_details.get("ResponseURL")
        # Return internal values
        return parsed_data

    def update_or_create_messages(self, results: list) -> QuerySet:
        """
        Updates or creates messages.
        """
        # Split messages by id list
        results = [
            results[i : i + self.MESSAGES_CHUNK]
            for i in range(0, len(results), self.MESSAGES_CHUNK)
        ]
        detailed_messages = list()
        # Get all data from messages by calling action again for each chunk of id list
        for messages in results:
            message_ids = [message["MessageID"] for message in messages]
            is_success, message, objects = self.raisable_action(
                GetEbayMessageList,
                message_ids=message_ids,
                detail_level="ReturnMessages",
            )
            detailed_messages += [
                self.parse_message_data(m) for m in objects["results"]
            ]

        serializer = DownloadEbayMessageSerializer(data=detailed_messages, many=True)
        serializer.is_valid(raise_exception=True)

        qs = serializer.save(marketplace_user_account=self.marketplace_user_account)
        return qs

    def success_trigger(self, message, objects, **kwargs):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        objects["results"] = self.update_or_create_messages(objects["results"])
        return is_success, message, objects


class CountNewEbayMessages(GetEbayMessageList):
    def get_params(self, days_ago=None, **kwargs):
        kwargs["days_ago"] = days_ago
        kwargs["detail_level"] = "ReturnSummary"
        return super().get_params(**kwargs)

    def success_trigger(self, message, objects, **kwargs):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        objects["results"] = objects["results"]["NewMessageCount"]
        return is_success, message, objects


class GetEbayMessage(GetEbayMessageList):
    def get_params(self, message_id, show_body=True, **kwargs):
        kwargs["message_ids"] = [message_id]
        kwargs["detail_level"] = "ReturnMessages" if show_body else "ReturnHeaders"
        return super().get_params(**kwargs)

    def success_trigger(self, message, objects, **kwargs):
        is_success, message, objects = super().success_trigger(
            message, objects, **kwargs
        )
        if not objects["results"]:
            objects["errors"] = objects.pop("warnings", objects.get("warnings", None))
            return super().failure_trigger(message, objects, **kwargs)
        objects["results"] = objects["results"][0]
        return is_success, message, objects


class GetEbayMemberMessageList(EbayTradingAPIAction):
    """
    GetMemberMessages:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/GetMemberMessages.html
    """

    verb = "GetMemberMessages"

    def get_params(
        self,
        message_type="All",
        message_status=None,
        item_id=None,
        sender_id=None,
        days_ago=30,
        **kwargs,
    ):
        if message_type not in ["All", "AskSellerQuestion"]:
            raise AttributeError('Недопустимое значение параметра "message_type"')

        params = {"MailMessageType": message_type}

        if message_status:
            if not (message_status in ["Answered", "Unanswered"]):
                raise AttributeError('Недопустимое значение параметра "message_status"')
            params.update({"MessageStatus": message_status})

        if item_id:
            params.update({"ItemID": item_id})
        elif sender_id:
            params.update({"SenderID": sender_id})
        else:
            if not 0 <= days_ago <= 90:
                raise AttributeError('Недопустимое значение параметра "days_ago"')
            end_creation_time = datetime.datetime.now()
            start_creation_time = end_creation_time - datetime.timedelta(days=days_ago)

            params.update(
                {
                    "EndCreationTime": end_creation_time,
                    "StartCreationTime": start_creation_time,
                }
            )

        return params

    def success_trigger(self, message, objects, **kwargs):
        results = objects["results"]["MemberMessage"]["MemberMessageExchange"]
        if not isinstance(results, list):
            results = [results]
        objects["results"] = results
        return super().success_trigger(message, objects, **kwargs)


class ReviseEbayMessages(EbayTradingAPIAction):
    """
    ReviseMyMessages:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/ReviseMyMessages.html
    """

    verb = "ReviseMyMessages"

    def get_params(self, message_ids: list, read: bool, **kwargs):
        return {
            "MessageIDs": {"MessageID": message_ids,},
            "Read": read,
        }


class MarkEbayMessageRead(ReviseEbayMessages):
    def get_params(self, message_id: str, **kwargs):
        kwargs["message_ids"] = [message_id]
        kwargs["read"] = True
        return super().get_params(**kwargs)


class AbstractSendEbayMessage(EbayTradingAPIAction):
    """
    Abstract class.
    """

    def get_params(
        self,
        message_body: str,
        parent_message_id: str,
        item_id: str = None,
        recipient_id: str = None,
        email_copy_to_sender: bool = False,
        message_media=None,
        **kwargs,
    ):
        if message_media:
            raise AttributeError("Прикрепление фотографий не поддерживается")

        params = {
            "MemberMessage": {
                "Body": message_body,
                "EmailCopyToSender": email_copy_to_sender,
                "ParentMessageID": parent_message_id,
                "RecipientID": recipient_id,
            },
            "ItemID": item_id,
        }

        return params


class SendEbayMessage(AbstractSendEbayMessage):
    """
    AddMemberMessageRTQ:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/AddMemberMessageRTQ.html
    """

    verb = "AddMemberMessageRTQ"

    def get_params(
        self,
        item_id: str = None,
        recipient_id: str = None,
        display_to_public=False,
        **kwargs,
    ):
        if not item_id:
            display_to_public = False
            if not recipient_id:
                raise AttributeError('Необходимо задать "recipient_id" или "item_id"')

        params = super().get_params(
            item_id=item_id, recipient_id=recipient_id, **kwargs
        )

        if not params.get("item_id", None):
            params["MemberMessage"].update({"DisplayToPublic": display_to_public})

        return params


class ReplyEbayMessage(SendEbayMessage):
    def get_parent_message(self, parent_message_id: str):
        is_success, message, objects = self.raisable_action(
            GetEbayMessage, message_id=parent_message_id
        )
        return objects["results"]

    def get_params(self, message_id: str, **kwargs):
        parent_message_data = self.get_parent_message(parent_message_id=message_id)
        kwargs["parent_message_id"] = message_id
        kwargs["recipient_id"] = parent_message_data["Sender"]
        kwargs["parent_message_id"] = parent_message_data["ExternalMessageID"]
        return super().get_params(**kwargs)


class AnswerEbayOrderMessage(AbstractSendEbayMessage):
    """
    AddMemberMessageAAQToPartner:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/AddMemberMessageAAQToPartner.html
    HINT: item needs to be a part of an offer
    """

    verb = "AddMemberMessageAAQToPartner"

    question_type_enum = [
        "CustomizedSubject",
        "General",
        "MultipleItemShipping",
        "None",
        "Payment",
        "Shipping",
    ]

    def get_params(
        self, item_id, recipient_id, subject, question_type="None", **kwargs
    ):
        if not (question_type in self.question_type_enum):
            raise AttributeError('Недопустимое значение параметра "question_type"')

        params = super().get_params(**kwargs)
        params["MemberMessage"].update(
            {"QuestionType": question_type, "Subject": subject,}
        )
        return params


class SendEbayBestOfferMessage(AbstractSendEbayMessage):
    """
    AddMemberMessagesAAQToBidder:
    https://developer.ebay.com/Devzone/XML/docs/Reference/eBay/AddMemberMessagesAAQToBidder.html
    HINT: item needs to be tested
    """

    verb = "AddMemberMessagesAAQToBidder"

    def get_params(self, **kwargs):
        params = super().get_params(**kwargs)
        params.update({"CorrelationID": "1"})
        return params
