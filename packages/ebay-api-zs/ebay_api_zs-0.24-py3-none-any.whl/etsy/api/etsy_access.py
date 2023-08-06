from django.conf import settings
from django.utils import timezone

from etsy.api.etsy_api import EtsyEnvProduction, EtsyEnvSandbox
from etsy_oauth.oauth_client import EtsyOAuthClient, EtsyOAuthClientError

from zonesmart.marketplace.api.marketplace_access import MarketplaceAPIAccess
from zonesmart.utils.logger import get_logger

logger = get_logger(__name__)


def now_plus_five_minutes():
    return timezone.now() + timezone.timedelta(minutes=5)


class EtsyAPIAccessError(Exception):
    pass


class EtsyAPIAccess(MarketplaceAPIAccess):
    marketplace_name = "Etsy"
    exception_class = EtsyAPIAccessError

    @property
    def is_sandbox(self):
        return settings.ETSY_SANDBOX

    @property
    def oauth_env(self):
        if self.is_sandbox:
            return EtsyEnvSandbox()
        else:
            return EtsyEnvProduction()

    @property
    def scopes(self):
        return settings.ETSY_API_SCOPES

    @property
    def oauth_callback(self):
        url = settings.ETSY_OAUTH_CALLBACK
        if not url:
            url = "oob"
        return url

    @property
    def credentials(self):
        return settings.ETSY_APP_CONFIG

    @property
    def client(self):
        if not getattr(self, "_client", None):
            self._client = EtsyOAuthClient(
                oauth_consumer_key=self.credentials["api_key"],
                oauth_consumer_secret=self.credentials["secret"],
                oauth_env=self.oauth_env,
                token=getattr(self.account, "token", None),
            )
        return self._client

    def get_temp_token(self):
        try:
            temp_token = self.client.get_request_token(
                scope=" ".join(self.scopes), oauth_callback=self.oauth_callback,
            )
        except EtsyOAuthClientError as error:
            raise self.exception_class(str(error))
        return temp_token

    def get_auth_url(self, temp_access_token):
        return self.client.get_signin_url(temp_access_token=temp_access_token)

    def get_user_token_data(
        self,
        oauth_verifier: str,
        temp_access_token: str,
        temp_access_token_secret: str,
    ):
        if (not temp_access_token) or (not temp_access_token_secret):
            raise self.exception_class(
                "Необходимо задать 'temp_access_token' и 'temp_access_token_secret'."
            )
        try:
            token = self.client.get_access_token(
                oauth_verifier=oauth_verifier,
                temp_access_token=temp_access_token,
                temp_access_token_secret=temp_access_token_secret,
            )
        except EtsyOAuthClientError as error:
            raise self.exception_class(str(error))
        return token

    def set_marketplace_user_account(self, **kwargs):
        marketplace_user_account = super().set_marketplace_user_account(**kwargs)
        if (not self.channel) and marketplace_user_account:
            if marketplace_user_account.channels.count() == 1:
                self.channel = marketplace_user_account.channels.first()
        return marketplace_user_account
