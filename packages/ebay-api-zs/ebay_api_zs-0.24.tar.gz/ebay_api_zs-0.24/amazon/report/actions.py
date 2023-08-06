from amazon.api.amazon_action import AmazonReportAction
from amazon.utils import jsonify_object_dict
from ftfy import fix_encoding  # noqa: F401


class GetReportRequestList(AmazonReportAction):
    def make_request(self, **query_params):
        is_success, message, objects = self.api.get_report_request_list(**query_params)
        if is_success:
            message = f"Список запросов на отчеты Amazon успешно получен.\n{message}"
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["ReportRequestInfo"]
            )
        else:
            message = f"Не удалось получить список запросов на отчеты.\n{message}"
        return is_success, message, objects


class GetReportList(AmazonReportAction):
    def make_request(self, **query_params):
        is_success, message, objects = self.api.get_report_list(**query_params)
        if is_success:
            message = f"Список отчетов Amazon успешно получен.\n{message}"
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["ReportInfo"]
            )
        else:
            message = f"Не удалось получить список отчетов Amazon.\n{message}"
        return is_success, message, objects


class GetReport(AmazonReportAction):
    def make_request(self, report_id, report_type=None, **kwargs):
        is_success, message, objects = self.api.get_report(report_id, **kwargs)
        if is_success:
            message = f"Отчет Amazon успешно получен.\n{message}"

            # Browse Tree Report bug fix
            if report_type == "_GET_XML_BROWSE_TREE_DATA_":
                objects["response"]._rootkey = ""
                objects["results"] = jsonify_object_dict(
                    objects["response"].parsed["Node"]
                )
            else:
                objects["results"] = objects["response"].parsed.decode(
                    "sloppy-windows-1252"
                )
        else:
            message = f"Не удалось получить отчет Amazon.\n{message}"
        return is_success, message, objects


class RequestReport(AmazonReportAction):
    def make_request(self, **query_params):
        is_success, message, objects = self.api.request_report(**query_params)
        if is_success:
            message = f"Отчет Amazon успешно получен.\n{message}"
            objects["results"] = jsonify_object_dict(
                objects["response"].parsed["ReportRequestInfo"]
            )
        else:
            message = f"Не удалось получить отчет Amazon.\n{message}"
        return is_success, message, objects
