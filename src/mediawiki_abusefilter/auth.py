import requests

from .exceptions import FilterError, LoginError


DEFAULT_USER_AGENT = "mediawiki-abusefilter/0.1.3 (madmax.wp@proton.me)"


class Auth:
    """Handle authentication and the HTTP session used by the client."""

    def __init__(self, url, username=None, password=None, session=None, timeout=30, tls_verify=True, user_agent=DEFAULT_USER_AGENT, debug=False):
        """Create an authentication session for a MediaWiki site."""
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self.tls_verify = tls_verify
        self.debug = debug
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self._logged_in = False
        self._api_url = None
        if username is not None or password is not None:
            self.login()

    @property
    def api_url(self):
        """Return the MediaWiki API URL."""
        if self._api_url is None:
            params = {"action": "query", "meta": "siteinfo", "siprop": "general", "format": "json", "formatversion": 2}
            self._api_url = f"{self.url}/w/api.php"
            response = self.session.get(self._api_url, params=params, timeout=self.timeout, verify=self.tls_verify)
            response.raise_for_status()
            self._debug(f"api url: {self._api_url}")
        return self._api_url

    def _debug(self, message):
        if self.debug:
            print(f"[mediawiki-abusefilter] {message}")

    def login(self, force=False):
        """Authenticate the configured account and reuse an existing login when possible."""
        if self._logged_in and not force:
            self._debug("login: already logged in")
            return self
        if not self.username or self.password is None:
            raise ValueError("username and password must be supplied for login")
        self._debug("login: requesting login token")
        response = self.session.get(self.api_url, params={"action": "query", "meta": "tokens", "type": "login", "format": "json", "formatversion": 2}, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        self._debug(f"login token: OK ({response.status_code})")
        payload = response.json()
        try:
            token = payload["query"]["tokens"]["logintoken"]
        except KeyError as exc:
            self._debug("login token: FAILED")
            raise LoginError(f"could not get login token: {payload}") from exc
        self._debug("login: submitting credentials")
        response = self.session.post(self.api_url, data={"action": "login", "lgname": self.username, "lgpassword": self.password, "lgtoken": token, "format": "json"}, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        payload = response.json()
        result = payload.get("login", {})
        if result.get("result") != "Success":
            self._debug(f"login: FAILED ({result.get('result', 'unknown')})")
            raise LoginError(result.get("reason") or result.get("message") or payload)
        self._logged_in = True
        self.username = result.get("lgusername") or self.username
        self._debug(f"login: OK as {self.username}")
        return self

    def whoami(self):
        """Return information about the current account."""
        response = self.session.get(self.api_url, params={"action": "query", "meta": "userinfo", "uiprop": "groups|rights", "format": "json", "formatversion": 2}, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            error = payload["error"]
            code = str(error.get("code", "")).lower()
            if code in {"notloggedin", "notoken", "mustbeloggedin", "badaccess", "permissiondenied"} or "login" in code or "auth" in code:
                raise LoginError(error.get("info", str(error)))
            raise FilterError(error.get("info", str(error)))
        return payload.get("query", {}).get("userinfo", {})
