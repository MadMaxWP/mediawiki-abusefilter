import re
from datetime import datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .exceptions import FilterError, FilterSaveError
from .rules import apply_rules


class Filter:
    """Represent one MediaWiki AbuseFilter."""

    def __init__(self, client, filter_id, data=None, public=None, metadata=None):
        self._client = client
        self.id = int(filter_id)
        self._data = data or {}
        self._public = public
        self._metadata = metadata or {}

    @property
    def description(self):
        """Return the filter description."""
        return self._data.get("wpFilterDescription", self._metadata.get("description", ""))

    @property
    def rules(self):
        """Return the current filter expression."""
        return self._data.get("wpFilterRules", self._metadata.get("pattern", "")).strip()

    @property
    def notes(self):
        """Return the filter notes."""
        return self._data.get("wpFilterNotes", self._metadata.get("comments", "")).strip()

    @property
    def enabled(self):
        """Return whether the filter is enabled."""
        return "wpFilterEnabled" in self._data if self._data else bool(self._metadata.get("enabled", False))

    @property
    def public(self):
        """Return whether the filter is public."""
        return bool(self._public) if self._public is not None else bool(self._metadata.get("public", True))

    @property
    def actions(self):
        """Return the configured actions."""
        if not self._data:
            return self._metadata.get("actions", "")
        actions = {}
        if "wpFilterActionWarn" in self._data:
            value = self._data.get("wpFilterWarnMessage", "")
            actions["warn"] = self._data.get("wpFilterWarnMessageOther", "") if value == "other" else value
        if "wpFilterActionDisallow" in self._data:
            value = self._data.get("wpFilterDisallowMessage", "")
            actions["disallow"] = self._data.get("wpFilterDisallowMessageOther", "") if value == "other" else value
        if "wpFilterActionBlockautopromote" in self._data:
            actions["blockautopromote"] = True
        if "wpFilterActionBlock" in self._data:
            actions["block"] = {
                "talk": "wpFilterBlockTalk" in self._data,
                "anon_duration": self._data.get("wpBlockAnonDuration", ""),
                "user_duration": self._data.get("wpBlockUserDuration", ""),
            }
        if "wpFilterActionTag" in self._data:
            actions["tag"] = [x.strip() for x in self._data.get("wpFilterTags", "").split(",") if x.strip()]
        if "wpFilterActionThrottle" in self._data:
            actions["throttle"] = {
                "count": self._data.get("wpFilterThrottleCount", ""),
                "period": self._data.get("wpFilterThrottlePeriod", ""),
                "groups": self._data.get("wpFilterThrottleGroups", "").strip(),
            }
        return actions

    @property
    def hits(self):
        """Return the recorded hit count when available."""
        return self._metadata.get("hits")

    @property
    def last_editor(self):
        """Return the most recent editor when available."""
        return self._metadata.get("lasteditor")

    @property
    def last_edit_time(self):
        """Return the most recent edit time when available."""
        return self._metadata.get("lastedittime")

    @property
    def protected(self):
        """Return whether the filter is protected."""
        return bool(self._metadata.get("protected", False))

    @property
    def suppressed(self):
        """Return whether the filter is suppressed."""
        return bool(self._metadata.get("suppressed", False))

    def history(self, limit=50):
        """Return the filter's edit history."""
        if int(limit) < 1:
            raise ValueError("limit must be at least 1")
        url = self._client._special_url(f"Special:AbuseFilter/history/{self.id}")
        self._client._debug(f"history: requesting filter {self.id}")
        response = self._client.session.get(url, timeout=self._client.timeout, verify=self._client.tls_verify)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            self._client._debug("history: OK (0 entries)")
            return []
        entries = []
        # the first row is the history table header
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["th", "td"])
            if len(cells) < 6:
                continue
            item_url = next((a.get("href") for a in cells[0].find_all("a", href=True) if re.search(r"/history/\d+/item/\d+", a.get("href", ""))), None)
            diff_url = next((a.get("href") for a in cells[5].find_all("a", href=True) if "/history/" in a.get("href", "") and "/diff/" in a.get("href", "")), None)
            revision = re.search(r"/item/(\d+)", item_url or "")
            flags = [value.strip() for value in cells[3].get_text(" ", strip=True).split(",") if value.strip()]
            entries.append({
                "id": int(revision.group(1)) if revision else None,
                "timestamp": cells[0].get_text(" ", strip=True),
                "user": cells[1].get_text(" ", strip=True),
                "description": cells[2].get_text(" ", strip=True),
                "flags": flags,
                "actions": cells[4].get_text(" ", strip=True),
                "item_url": urljoin(response.url, item_url) if item_url else None,
                "diff_url": urljoin(response.url, diff_url) if diff_url else None,
            })
            if len(entries) >= int(limit):
                break
        self._client._debug(f"history: OK ({len(entries)} entries)")
        return entries

    def refresh(self):
        """Reload the filter and return this object."""
        fresh = self._client.get(self.id)
        self._data = fresh._data
        self._public = fresh._public
        self._metadata = fresh._metadata
        return self

    def edit(self, rules=None, description=None, notes=None, enabled=None, public=None, actions=None, replace=None, append=None, prepend=None, remove=None, regex=None, strict=True, verify=True, dry_run=False, sign_notes=False, notes_mode="append"):
        """Update one or more filter settings and return this object."""
        if notes_mode not in {"append", "replace"}:
            raise ValueError("notes_mode must be 'append' or 'replace'")
        soup, form, data = self._client._get_edit_form(self.id)
        old_rules = data.get("wpFilterRules", "").strip()
        new_rules = old_rules if rules is None else rules
        new_rules = apply_rules(new_rules, replace=replace, append=append, prepend=prepend, remove=remove, regex=regex, strict=strict)
        data["wpFilterRules"] = new_rules
        if description is not None:
            data["wpFilterDescription"] = description
        if notes is not None:
            new_notes = str(notes).strip()
            if new_notes and sign_notes:
                user = self._client.auth.username
                if not user:
                    user = self._client.whoami().get("name")
                if user:
                    new_notes = f"{new_notes} - {user} {datetime.now().strftime('%d %B %Y').lstrip('0')}"
            if notes_mode == "append":
                current_notes = data.get("wpFilterNotes", "").strip()
                data["wpFilterNotes"] = "\n".join(value for value in (current_notes, new_notes) if value)
            else:
                data["wpFilterNotes"] = new_notes
        if enabled is not None:
            if enabled:
                data["wpFilterEnabled"] = data.get("wpFilterEnabled", "")
            else:
                data.pop("wpFilterEnabled", None)
        self._client._apply_actions(data, actions)
        expected_actions = Filter(self._client, self.id, data=data, public=self.public, metadata=self._metadata).actions if actions is not None else None
        if public is not None:
            if public:
                data.pop("wpFilterHidden", None)
            else:
                data["wpFilterHidden"] = data.get("wpFilterHidden", "")
        if dry_run:
            return self._client._preview(self.id, old_rules, data)
        response = self._client._save_form(form, data, response_url=f"{self._client.url}/w/index.php/Special:AbuseFilter/{self.id}")
        if public is True and self._client._needs_public_confirmation(response.text):
            _, confirm_form, confirm_data = self._client._parse_form(response.text)
            confirm_data.pop("wpFilterHidden", None)
            response = self._client._save_form(confirm_form, confirm_data, response_url=response.url)
        self._client._require_success(response)
        self.refresh()
        if verify:
            if rules is not None or any(value is not None for value in (replace, append, prepend, remove, regex)):
                if self.rules != new_rules.strip():
                    raise FilterSaveError("rules verification failed")
            if description is not None and self.description != description:
                raise FilterSaveError("description verification failed")
            if notes is not None:
                expected_notes = data.get("wpFilterNotes", "").strip()
                if self.notes != expected_notes:
                    raise FilterSaveError("notes verification failed")
            if enabled is not None and self.enabled != enabled:
                raise FilterSaveError("enabled verification failed")
            if public is not None and self.public != public:
                raise FilterSaveError("public verification failed")
            if actions is not None and self.actions != expected_actions:
                raise FilterSaveError("actions verification failed")
        return self

    def save(self, **changes):
        """Save changes using the same interface as edit()."""
        return self.edit(**changes)

    def delete(self):
        """Delete the filter when the current account has permission."""
        soup, form, data = self._client._get_edit_form(self.id)
        field = form.select_one('[name="wpFilterDeleted"]')
        if not field or field.has_attr("disabled"):
            raise FilterError("this wiki does not allow the current user to delete this filter")
        data["wpFilterDeleted"] = field.get("value", "")
        response = self._client._save_form(form, data, response_url=f"{self._client.url}/w/index.php/Special:AbuseFilter/{self.id}")
        self._client._require_success(response)
        return True
