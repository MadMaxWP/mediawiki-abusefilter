from datetime import datetime

from mediawiki_abusefilter.filter import Filter


class FakeClient:
    def __init__(self):
        self.auth = type("Auth", (), {"username": "DR"})()
        self.data = {"wpFilterNotes": "old note"}

    def _get_edit_form(self, filter_id):
        return None, object(), self.data.copy()

    def _apply_actions(self, data, actions):
        pass

    def whoami(self):
        return {"name": "DR"}

    def _debug(self, message):
        pass

    def _preview(self, filter_id, old_rules, data):
        return data

    def get(self, filter_id):
        return Filter(self, filter_id, data=self.data.copy())


def test_notes_append_without_signature():
    client = FakeClient()
    filter = Filter(client, 1, data={"wpFilterNotes": "old note", "wpFilterRules": "false"})
    result = filter.edit(notes="new note", dry_run=True)
    assert result["wpFilterNotes"] == "old note\nnew note"


def test_notes_append_with_signature(monkeypatch):
    class FixedDate(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 2, 23)

    monkeypatch.setattr("mediawiki_abusefilter.filter.datetime", FixedDate)
    client = FakeClient()
    filter = Filter(client, 1, data={"wpFilterNotes": "old note", "wpFilterRules": "false"})
    result = filter.edit(notes="new note", sign_notes=True, dry_run=True)
    assert result["wpFilterNotes"] == "old note\nnew note - DR 23 February 2026"


def test_notes_replace_and_clear():
    client = FakeClient()
    filter = Filter(client, 1, data={"wpFilterNotes": "old note", "wpFilterRules": "false"})
    result = filter.edit(notes="replacement", notes_mode="replace", dry_run=True)
    assert result["wpFilterNotes"] == "replacement"
    result = filter.edit(notes="", notes_mode="replace", dry_run=True)
    assert result["wpFilterNotes"] == ""
