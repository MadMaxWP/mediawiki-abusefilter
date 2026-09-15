import re
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup

from .auth import Auth, DEFAULT_USER_AGENT
from .exceptions import FilterError, FilterNotFoundError, FilterPermissionError, FilterSaveError, FilterSyntaxError, ValidationError
from .filter import Filter
from .forms import form_action, parse_form


class Filters:
    """Client for finding, creating, and managing MediaWiki AbuseFilters."""

    def __init__(self, url, username=None, password=None, session=None, timeout=30, tls_verify=True, user_agent=DEFAULT_USER_AGENT, debug=False, auth=None):
        """Create a client for one MediaWiki site."""
        self.url = url.rstrip("/")
        if auth is not None and any(value is not None for value in (username, password, session)):
            raise ValueError("auth cannot be combined with username, password, or session")
        self.auth = auth or Auth(self.url, username=username, password=password, session=session, timeout=timeout, tls_verify=tls_verify, user_agent=user_agent, debug=debug)
        if debug and not self.auth.debug:
            self.auth.debug = True
        self.username = self.auth.username
        self.password = self.auth.password
        self.timeout = self.auth.timeout
        self.tls_verify = self.auth.tls_verify
        self.debug = self.auth.debug
        self.session = self.auth.session

    def _debug(self, message):
        if self.debug:
            print(f"[mediawiki-abusefilter] {message}")

    @property
    def api_url(self):
        """Return the MediaWiki API URL."""
        return self.auth.api_url

    def _special_url(self, title):
        return urljoin(f"{self.url}/", f"w/index.php/{title}")

    def login(self):
        """Authenticate the configured account and return this client."""
        self.auth.login()
        self.username = self.auth.username
        return self

    def whoami(self):
        """Return information about the currently authenticated account."""
        self._debug("whoami: requesting current user")
        result = self.auth.whoami()
        self._debug(f"whoami: {result.get('name', '(not logged in)')}")
        return result

    def list(self, limit=50, enabled=None, public=None, private=None, protected=None, suppressed=None, start=None, end=None, direction=None):
        """Return filters matching the supplied criteria."""
        if int(limit) < 1:
            raise ValueError("limit must be at least 1")
        if direction not in (None, "older", "newer"):
            raise ValueError("direction must be 'older', 'newer', or None")
        checks = {"enabled": enabled, "public": public, "private": private, "protected": protected, "suppressed": suppressed}
        for key, value in checks.items():
            if value is not None and not isinstance(value, bool):
                raise TypeError(f"{key} must be True, False, or None")
        remaining = int(limit)
        cursor = None
        params_base = {
            "action": "query",
            "list": "abusefilters",
            "abfprop": "id|description|pattern|actions|hits|comments|lasteditor|lastedittime|status|private|protected|suppressed",
            "format": "json",
            "formatversion": 2,
        }
        result = []
        while remaining > 0:
            params = dict(params_base)
            params["abflimit"] = min(remaining, 500)
            if start is not None:
                params["abfstartid"] = int(start)
            if end is not None:
                params["abfendid"] = int(end)
            if direction is not None:
                params["abfdir"] = direction
            if cursor:
                params.update(cursor)
            self._debug(f"list: requesting up to {params['abflimit']} filters")
            response = self.session.get(self.api_url, params=params, timeout=self.timeout, verify=self.tls_verify)
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                self._debug("list: FAILED")
                raise FilterError(payload["error"].get("info", str(payload["error"])))
            items = payload.get("query", {}).get("abusefilters", [])
            if not items and not payload.get("continue"):
                break
            for item in items:
                private_value = bool(item.get("private", False))
                protected_value = bool(item.get("protected", False))
                suppressed_value = bool(item.get("suppressed", False))
                values = dict(item)
                values["enabled"] = item.get("status") == "enabled"
                values["private"] = private_value
                values["public"] = not private_value
                values["protected"] = protected_value
                values["suppressed"] = suppressed_value
                if any(value is not None and values.get(key) != value for key, value in checks.items()):
                    continue
                result.append(Filter(self, item["id"], metadata=values))
                remaining -= 1
                if remaining == 0:
                    break
            next_continue = payload.get("continue")
            if remaining == 0 or not next_continue:
                break
            cursor = {key: value for key, value in next_continue.items() if key != "continue"}
            cursor["continue"] = next_continue.get("continue", "-||")
            start = None
            end = None
        self._debug(f"list: OK ({len(result)} filters)")
        return result

    def search(self, query, limit=50):
        """Search filter descriptions, rules, notes, actions, and last editors."""
        if not str(query).strip():
            raise ValueError("query must not be empty")
        if int(limit) < 1:
            raise ValueError("limit must be at least 1")
        needle = str(query).casefold()
        self._debug(f"search: looking for {query!r}")
        matches = []
        cursor = None
        while len(matches) < int(limit):
            params = {"limit": 500}
            if cursor:
                params.update(cursor)
            page = self._list_page(**params)
            for item in page[0]:
                values = [item.description, item.rules, item.notes, item.actions, item.last_editor]
                if needle in "\n".join(str(value or "") for value in values).casefold():
                    matches.append(item)
                    if len(matches) >= int(limit):
                        break
            cursor = page[1]
            if not cursor:
                break
        self._debug(f"search: OK ({len(matches)} filters)")
        return matches

    def _list_page(self, limit=500, **kwargs):
        params = {
            "action": "query",
            "list": "abusefilters",
            "abfprop": "id|description|pattern|actions|hits|comments|lasteditor|lastedittime|status|private|protected|suppressed",
            "abflimit": min(int(limit), 500),
            "format": "json",
            "formatversion": 2,
        }
        params.update({key: value for key, value in kwargs.items() if value is not None})
        response = self.session.get(self.api_url, params=params, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        payload = response.json()
        if "error" in payload:
            raise FilterError(payload["error"].get("info", str(payload["error"])))
        result = []
        for item in payload.get("query", {}).get("abusefilters", []):
            private_value = bool(item.get("private", False))
            values = dict(item)
            values["enabled"] = item.get("status") == "enabled"
            values["private"] = private_value
            values["public"] = not private_value
            values["protected"] = bool(item.get("protected", False))
            values["suppressed"] = bool(item.get("suppressed", False))
            result.append(Filter(self, item["id"], metadata=values))
        continuation = payload.get("continue")
        if not continuation:
            return result, None
        return result, {key: value for key, value in continuation.items()}

    def get(self, filter_id):
        """Return one filter with its current metadata and editable state."""
        filter_id = int(filter_id)
        page, _ = self._list_page(limit=1, abfstartid=filter_id, abfendid=filter_id)
        if not page:
            raise FilterNotFoundError(f"filter {filter_id} not found")
        metadata = page[0]._metadata
        url = self._special_url(f"Special:AbuseFilter/{filter_id}")
        response = self.session.get(url, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        try:
            soup, form, data = parse_form(response.text)
        except FilterError as exc:
            text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True)
            lower = text.lower()
            if "filter" in lower and any(value in lower for value in ("not found", "does not exist", "no such abuse filter", "no such filter")):
                raise FilterNotFoundError(f"filter {filter_id} not found") from exc
            raise
        metadata["public"] = "wpFilterHidden" not in data
        return Filter(self, filter_id, data=data, public=metadata["public"], metadata=metadata)

    def create(self, description, rules, notes=None, enabled=True, public=True, actions=None, verify=True, sign_notes=False, dry_run=False, notes_mode="append"):
        """Create a new AbuseFilter and return it, or preview it with dry_run."""
        if notes_mode not in {"append", "replace"}:
            raise ValueError("notes_mode must be 'append' or 'replace'")
        response = self.session.get(self._special_url("Special:AbuseFilter/new"), timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        soup, form, data = parse_form(response.text)
        data["wpFilterDescription"] = description
        data["wpFilterRules"] = rules
        note_text = str(notes).strip() if notes is not None else ""
        if note_text and sign_notes:
            user = self.auth.username
            if not user:
                user = self.whoami().get("name")
            if user:
                note_text = f"{note_text} - {user} {datetime.now().strftime('%d %B %Y').lstrip('0')}"
        data["wpFilterNotes"] = note_text
        if enabled:
            data["wpFilterEnabled"] = data.get("wpFilterEnabled", "")
        else:
            data.pop("wpFilterEnabled", None)
        self._apply_actions(data, actions)
        expected_actions = Filter(self, 0, data=data, public=public).actions if actions is not None else None
        if public:
            data.pop("wpFilterHidden", None)
        else:
            data["wpFilterHidden"] = data.get("wpFilterHidden", "")
        if dry_run:
            return self._preview(None, "", data)
        response = self._save_form(form, data, response.url)
        if self._needs_public_confirmation(response.text):
            _, confirm_form, confirm_data = self._parse_form(response.text)
            confirm_data.pop("wpFilterHidden", None)
            response = self._save_form(confirm_form, confirm_data, response.url)
        self._require_success(response, creating=True)
        query = parse_qs(urlparse(response.url).query)
        filter_id = int(query["changedfilter"][0]) if "changedfilter" in query else self._extract_changed_filter(response.text)
        filter = self.get(filter_id)
        if verify:
            if filter.description != description:
                raise FilterSaveError("create verification failed: description")
            if filter.rules != str(rules).strip():
                raise FilterSaveError("create verification failed: rules")
            if filter.notes != data.get("wpFilterNotes", "").strip():
                raise FilterSaveError("create verification failed: notes")
            if filter.enabled != enabled:
                raise FilterSaveError("create verification failed: enabled")
            if filter.public != public:
                raise FilterSaveError("create verification failed: public")
            if actions is not None and filter.actions != expected_actions:
                raise FilterSaveError("create verification failed: actions")
        return filter

    def _get_edit_form(self, filter_id):
        response = self.session.get(self._special_url(f"Special:AbuseFilter/{int(filter_id)}"), timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        return parse_form(response.text)

    def _parse_form(self, html):
        return parse_form(html)

    def _save_form(self, form, data, response_url):
        response = self.session.post(form_action(response_url, form), data=data, allow_redirects=True, timeout=self.timeout, verify=self.tls_verify)
        response.raise_for_status()
        return response

    def _require_success(self, response, creating=False):
        self._raise_if_error(response.text)
        text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True).lower()
        if "your changes to filter" in text and "have been saved" in text:
            return
        query = parse_qs(urlparse(response.url).query)
        if query.get("result") == ["success"] or "changedfilter" in query:
            return
        if self._needs_public_confirmation(response.text):
            return
        if getattr(response, "history", None) and not creating:
            return
        if not creating and BeautifulSoup(response.text, "html.parser").select_one('form#mw-abusefilter-editing-form'):
            return
        message = self._extract_error(response.text)
        target = "creation" if creating else "save"
        raise FilterSaveError(f"filter {target} did not complete successfully: {message}")

    def _raise_if_error(self, html):
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.select(".errorbox, .mw-message-box-error, .mw-abusefilter-error, .oo-ui-messageWidget-type-error, [role='alert']")
        body_text = soup.get_text(" ", strip=True)
        text = " ".join(node.get_text(" ", strip=True) for node in nodes).strip() or body_text
        lower = body_text.lower()
        if "there is a syntax error in the filter you specified" in lower:
            match = re.search(r"The output from the parser was:(.*?)(?:Filter parameters|Creating filter|Editing filter)", text, re.I)
            raise FilterSyntaxError(match.group(1).strip() if match else text[:1000])
        if "you do not have permission" in lower or "permission denied" in lower or "not authorized" in lower:
            raise FilterPermissionError(text[:1000])
        if "validation error" in lower:
            raise ValidationError(text[:1000])

    def _extract_error(self, html):
        soup = BeautifulSoup(html, "html.parser")
        error = soup.select_one('.errorbox, .mw-message-box-error, .mw-abusefilter-error, .oo-ui-messageWidget-type-error, [role="alert"]')
        if error:
            return error.get_text(" ", strip=True)[:1000]
        return soup.get_text(" ", strip=True)[:1000]

    def _extract_changed_filter(self, html):
        text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
        match = re.search(r"Your changes to filter\s+(\d+)\s+have been saved", text, re.I)
        if not match:
            match = re.search(r"changedfilter[=:](\d+)", html)
        if not match:
            raise FilterSaveError("could not determine the filter ID")
        return int(match.group(1))

    def _needs_public_confirmation(self, text):
        return "you are about to make a private filter public" in text.lower()

    def _preview(self, filter_id, old_rules, data):
        return {
            "filter_id": filter_id,
            "old_rules": old_rules.strip(),
            "new_rules": data.get("wpFilterRules", old_rules).strip(),
            "description": data.get("wpFilterDescription"),
            "notes": data.get("wpFilterNotes"),
            "enabled": "wpFilterEnabled" in data,
            "public": "wpFilterHidden" not in data,
        }

    def _apply_actions(self, data, actions):
        if not actions:
            return
        for name, value in actions.items():
            if name == "warn":
                if value is False:
                    data.pop("wpFilterActionWarn", None)
                else:
                    data["wpFilterActionWarn"] = ""
                    if value is not True:
                        if value in {"abusefilter-warning", "other"}:
                            data["wpFilterWarnMessage"] = value
                        else:
                            data["wpFilterWarnMessage"] = "other"
                            data["wpFilterWarnMessageOther"] = str(value)
            elif name == "disallow":
                if value is False:
                    data.pop("wpFilterActionDisallow", None)
                else:
                    data["wpFilterActionDisallow"] = ""
                    if value is not True:
                        if value in {"abusefilter-disallowed", "other"}:
                            data["wpFilterDisallowMessage"] = value
                        else:
                            data["wpFilterDisallowMessage"] = "other"
                            data["wpFilterDisallowMessageOther"] = str(value)
            elif name == "blockautopromote":
                if value:
                    data["wpFilterActionBlockautopromote"] = ""
                else:
                    data.pop("wpFilterActionBlockautopromote", None)
            elif name == "block":
                if value is False:
                    data.pop("wpFilterActionBlock", None)
                    data.pop("wpFilterBlockTalk", None)
                else:
                    options = value if isinstance(value, dict) else {}
                    data["wpFilterActionBlock"] = ""
                    if "talk" in options:
                        if options["talk"]:
                            data["wpFilterBlockTalk"] = ""
                        else:
                            data.pop("wpFilterBlockTalk", None)
                    if "anonymous" in options:
                        data["wpBlockAnonDuration"] = str(options["anonymous"])
                    elif "anon_duration" in options:
                        data["wpBlockAnonDuration"] = str(options["anon_duration"])
                    if "user" in options:
                        data["wpBlockUserDuration"] = str(options["user"])
                    elif "user_duration" in options:
                        data["wpBlockUserDuration"] = str(options["user_duration"])
            elif name == "tag":
                if value is False:
                    data.pop("wpFilterActionTag", None)
                    data.pop("wpFilterTags", None)
                else:
                    data["wpFilterActionTag"] = ""
                    data["wpFilterTags"] = ",".join(map(str, value)) if isinstance(value, (list, tuple, set)) else str(value)
            elif name == "throttle":
                if value is False:
                    data.pop("wpFilterActionThrottle", None)
                else:
                    options = value if isinstance(value, dict) else {}
                    data["wpFilterActionThrottle"] = ""
                    if "count" in options:
                        data["wpFilterThrottleCount"] = str(options["count"])
                    if "period" in options:
                        data["wpFilterThrottlePeriod"] = str(options["period"])
                    if "groups" in options:
                        groups = options["groups"]
                        data["wpFilterThrottleGroups"] = "\n".join(map(str, groups)) if isinstance(groups, (list, tuple, set)) else str(groups)
            else:
                raise ValueError(f"unknown action: {name}")
