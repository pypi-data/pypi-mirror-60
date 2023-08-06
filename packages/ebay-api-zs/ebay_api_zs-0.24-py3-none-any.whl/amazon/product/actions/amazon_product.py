from amazon.api.amazon_action import AmazonFeedAction
from amazon.report.actions import RequestReport
from amazon.utils import jsonify_object_dict


class SubmitAmazonFeed(AmazonFeedAction):
    def make_request(
        self, feed, feed_type="_POST_FLAT_FILE_LISTINGS_DATA_", **query_params
    ):
        if isinstance(feed, str):
            feed = feed.encode("sloppy-windows-1252")

        is_success, message, objects = self.api.submit_feed(
            feed=feed, feed_type=feed_type, **query_params
        )
        if is_success:
            message = f"Фид Amazon успешно отправлен на загрузку.\n{message}"
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["FeedSubmissionInfo"]
            )
        else:
            message = f"Не удалось отправить на загрузку фид Amazon.\n{message}"
        return is_success, message, objects


class GetAmazonFeedSubmissions(AmazonFeedAction):
    def make_request(self, **query_params):
        is_success, message, objects = self.api.get_feed_submission_list(**query_params)
        if is_success:
            message = f"Информация о загрузке фидов Amazon успешно получена.\n{message}"
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["FeedSubmissionInfo"]
            )
        else:
            message = (
                f"Не удалось получить информацию о загрузках фидов Amazon.\n{message}"
            )
        return is_success, message, objects


class CancelAmazonFeedSubmissions(AmazonFeedAction):
    def make_request(self, **query_params):
        is_success, message, objects = self.api.cancel_feed_submissions(**query_params)
        if is_success:
            message = f"Загрузка фидов Amazon успешно отменена.\n{message}"
            objects["results"] = [
                feed_info
                for feed_info in list(objects["response"].parsed["FeedSubmissionInfo"])
                if feed_info["FeedProcessingStatus"]["value"] == "_CANCELLED_"
            ]
        else:
            message = f"Не удалось отменить загрузку фидов Amazon.\n{message}"
        return is_success, message, objects


class GetAmazonFeedSubmissionResult(AmazonFeedAction):
    def make_request(self, feed_id):
        is_success, message, objects = self.api.get_feed_submission_result(feed_id)
        if is_success:
            message = f"Результат загрузки фида Amazon успешно получен.\n{message}"
            objects["results"] = objects["response"].parsed.decode()
        else:
            message = f"Не удалось получить результат загрузки фида Amazon.\n{message}"
        return is_success, message, objects


class RequestActiveListingsReport(RequestReport):
    def make_request(self, **query_params):
        query_params["report_type"] = "_GET_MERCHANT_LISTINGS_DATA_"
        return super().make_request(**query_params)
