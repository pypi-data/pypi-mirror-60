from datetime import datetime, timedelta

from etsy.account.models import EtsyUserAccount
from etsy.account.serializers.bill import (
    DownloadEtsyUserBillingOverviewSerializer,
    DownloadEtsyBillChargeSerializer,
)
from etsy.api.etsy_action import EtsyAccountAction
from etsy.api.etsy_api.actions.account import (
    GetUserChargesMetadata,
    FindAllUserCharges,
    GetUserBillingOverview,
)


class RemoteGetEtsyUserBillingOverview(EtsyAccountAction):
    api_class = GetUserBillingOverview


class RemoteDownloadUserBillingOverview(RemoteGetEtsyUserBillingOverview):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        # Init & validate serializer
        serializer = DownloadEtsyUserBillingOverviewSerializer(
            data=objects["results"][0]
        )
        serializer.is_valid(raise_exception=True)
        # Get EtsyUserAccount
        etsy_user_account = EtsyUserAccount.objects.get(
            marketplace_user_account=self.marketplace_user_account
        )
        # Save billing overview
        serializer.save(etsy_user_account=etsy_user_account)
        return super().success_trigger(message, objects, **kwargs)


class RemoteGetEtsyUserChargesMetadata(EtsyAccountAction):
    api_class = GetUserChargesMetadata


class RemoteGetEtsyUserChargeList(EtsyAccountAction):
    api_class = FindAllUserCharges

    def get_params(self, isoformat=True, **kwargs):
        if not kwargs.get("min_created", None):
            raise AttributeError(
                "Необходимо задать начало временного интервала 'min_created'."
            )

        for param in ["min_created", "max_created"]:
            value = kwargs.get(param, None)
            if value and isinstance(value, str):
                # case: value is isoformat
                try:
                    kwargs[param] = datetime.strptime(
                        value, "%Y-%m-%dT%H:%M:%S"
                    ).timestamp()
                except ValueError:
                    raise ValueError(
                        f"Параметр '{param}' может быть целым числом (UNIX epochs)"
                        f" или строкой (datetime в формате ISO)."
                    )

        return super().get_params(**kwargs)

    def make_request(self, **kwargs):
        page = 1
        results = []

        while True:
            kwargs["page"] = page
            print(f"Загрузка страницы {page}.")
            is_success, message, objects = super().make_request(
                **kwargs, raise_exception=True
            )
            results += objects["results"]
            page = objects["pagination"].get("next_page", None)
            if not page:
                break

        message = "Пользовательские транзакции Etsy успешно загружены."
        objects = {"count": len(results), "results": results}
        return True, message, objects


class RemoteGetFullEtsyUserChargeList(EtsyAccountAction):
    interval_length = 30

    def _to_date(self, value: int):
        return datetime.fromtimestamp(value).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    def get_charges_interval(self):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyUserChargesMetadata
        )
        return objects["results"]

    def get_charges(self, min_created, max_created):
        is_success, message, objects = self.raisable_action(
            RemoteGetEtsyUserChargeList,
            min_created=min_created,
            max_created=max_created,
        )
        return objects["results"]

    def make_request(self, **kwargs):
        metadata = self.get_charges_interval()
        if not metadata.get("count", 0):
            return True, "", {}

        min_created = self._to_date(metadata["min_create_date"])
        max_created = self._to_date(metadata["max_create_date"]) + timedelta(days=1)
        print(f"Полный интервал: {min_created} -- {max_created}")

        full_interval = (max_created - min_created).days
        results = []

        for i in range((full_interval // self.interval_length) + 1):
            left_border = min_created + timedelta(days=(self.interval_length * i))
            right_border = min(
                min_created + timedelta(days=(self.interval_length * (i + 1))),
                max_created,
            )
            if left_border >= right_border:
                break

            print(f"Интервал {i+1}: {left_border} -- {right_border}")
            results += self.get_charges(
                min_created=left_border, max_created=right_border
            )

        message = "Биллинговая информация аккаунта Etsy успешно загружена."
        objects = {"count": len(results), "results": results}
        return True, message, objects


class RemoteDownloadUserBillChargeList(RemoteGetEtsyUserChargeList):
    def success_trigger(self, message: str, objects: dict, **kwargs):
        # Init & validate serializer
        serializer = DownloadEtsyBillChargeSerializer(
            data=objects["results"], many=True
        )
        serializer.is_valid(raise_exception=True)
        # Get EtsyUserAccount
        etsy_user_account = EtsyUserAccount.objects.get(
            marketplace_user_account=self.marketplace_user_account
        )
        # Save charges
        serializer.save(etsy_user_account=etsy_user_account)
        return super().success_trigger(message, objects, **kwargs)
