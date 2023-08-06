from urllib.parse import parse_qsl, quote, urlencode

import oauth2 as oauth

EtsyOAuthToken = oauth.Token


class EtsyOAuthClientError(Exception):
    pass


class EtsyOAuthClient(oauth.Client):
    def __init__(
        self,
        oauth_consumer_key,
        oauth_consumer_secret,
        oauth_env,
        token=None,
        logger=None,
    ):
        consumer = oauth.Consumer(oauth_consumer_key, oauth_consumer_secret)
        super(EtsyOAuthClient, self).__init__(consumer)

        self.request_token_url = oauth_env.request_token_url
        self.access_token_url = oauth_env.access_token_url
        self.signin_url = oauth_env.signin_url
        self.token = token
        self.logger = logger

    def get_request_token(self, **kwargs):
        request_token_url = "%s?%s" % (
            self.request_token_url,
            urlencode(kwargs, quote_via=quote),
        )
        resp, content = self.request(request_token_url, "GET")
        return self._get_token(content)

    def get_signin_url(self, temp_access_token):
        return (
            self.signin_url
            + "?"
            + urlencode({"oauth_token": temp_access_token}, quote_via=quote)
        )

    def get_access_token(
        self, temp_access_token, temp_access_token_secret, oauth_verifier
    ):
        self.token = EtsyOAuthToken(temp_access_token, temp_access_token_secret)
        resp, content = self.request(
            f"{self.access_token_url}?oauth_verifier={oauth_verifier}", "GET"
        )
        self.token = None
        return self._get_token(content)

    def do_oauth_request(self, url, http_method, content_type, body):
        if content_type and content_type != "application/x-www-form-urlencoded":
            response, content = self.request(
                url, http_method, body=body, headers={"Content-Type": content_type}
            )
        else:
            response, content = self.request(url, http_method, body=body)

        if self.logger:
            self.logger.debug("do_oauth_request: content = %r" % content)

        return response, content

    def _get_token(self, content):
        d = dict(parse_qsl(content.decode()))
        try:
            return EtsyOAuthToken(d["oauth_token"], d["oauth_token_secret"])
        except KeyError:
            raise EtsyOAuthClientError(
                f"При попытке получения токена возникла ошибка: {d.get('oauth_problem', 'системная ошибка')}"
            )
