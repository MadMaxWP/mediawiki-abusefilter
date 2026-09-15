import inspect
from mediawiki_abusefilter.auth import Auth as RealAuth
from mediawiki_abusefilter.client import Filters
from mediawiki_abusefilter.exceptions import FilterPermissionError, FilterSaveError
from mediawiki_abusefilter.filter import Filter


class Response:
    def __init__(self, payload=None, text="", url="http://example.org/index.php/Special:AbuseFilter/1", history=None, status_code=200):
        self._payload = payload
        self.text = text
        self.url = url
        self.history = history or []
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.headers = {}
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return next(self.responses)

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return next(self.responses)


class DummyAuth:
    _api_url = "http://example.org/w/api.php"
    api_url = "http://example.org/w/api.php"
    username = "DR"
    debug = False
    timeout = 30
    tls_verify = True
    password = "password"
    session = None


class ExistingAuth:
    _api_url = "http://example.org/w/api.php"
    api_url = "http://example.org/w/api.php"
    username = "DR"
    debug = False
    timeout = 30
    tls_verify = False
    password = "password"
    session = None


def client_with(session):
    client = Filters.__new__(Filters)
    client.url = "http://example.org"
    client.auth = DummyAuth()
    client.auth.session = session
    client.username = "DR"
    client.password = "password"
    client.timeout = 30
    client.tls_verify = True
    client.debug = False
    client.session = session
    client._article_path = None
    return client


def test_auth_prefers_w_api():
    session = Session([Response({"query": {"general": {}}}, url="http://example.org/w/api.php")])
    auth = RealAuth.__new__(RealAuth)
    auth.url = "http://example.org"
    auth.username = None
    auth.password = None
    auth.timeout = 30
    auth.tls_verify = True
    auth.debug = False
    auth.session = session
    auth._api_url = None
    assert auth.api_url == "http://example.org/w/api.php"
    assert len(session.calls) == 1


def test_auth_falls_back_to_root_api_on_404():
    session = Session([
        Response(status_code=404),
        Response({"query": {"general": {}}}, url="http://example.org/api.php"),
    ])
    auth = RealAuth.__new__(RealAuth)
    auth.url = "http://example.org"
    auth.username = None
    auth.password = None
    auth.timeout = 30
    auth.tls_verify = True
    auth.debug = False
    auth.session = session
    auth._api_url = None
    assert auth.api_url == "http://example.org/api.php"
    assert [call[1] for call in session.calls] == ["http://example.org/w/api.php", "http://example.org/api.php"]


def test_client_uses_auth_api_url():
    session = Session([])
    client = client_with(session)
    client.auth.api_url = "http://example.org/custom/api.php"
    assert client.api_url == "http://example.org/custom/api.php"


def test_list_normalizes_booleans_and_uses_json_v2():
    session = Session([
        Response({
            "query": {
                "abusefilters": [{
                    "id": 1,
                    "description": "private",
                    "pattern": "false",
                    "status": "enabled",
                    "private": True,
                    "protected": True,
                    "suppressed": True,
                }]
            }
        })
    ])
    filters = client_with(session)
    result = filters.list()
    assert result[0].public is False
    assert result[0].enabled is True
    assert result[0].protected is True
    assert result[0].suppressed is True
    params = session.calls[0][2]["params"]
    assert params["formatversion"] == 2


def test_list_follows_continuation():
    session = Session([
        Response({
            "query": {"abusefilters": [
                {"id": 1, "description": "one"},
                {"id": 2, "description": "two"},
            ]},
            "continue": {"abfstartid": 3, "continue": "-||"},
        }),
        Response({
            "query": {"abusefilters": [
                {"id": 3, "description": "three"},
            ]}
        }),
    ])
    filters = client_with(session)
    result = filters.list(limit=3)
    assert [item.id for item in result] == [1, 2, 3]
    assert len(session.calls) == 2


def test_search_follows_continuation():
    session = Session([
        Response({
            "query": {"abusefilters": [
                {"id": 1, "description": "one"},
            ]},
            "continue": {"abfstartid": 2, "continue": "-||"},
        }),
        Response({
            "query": {"abusefilters": [
                {"id": 2, "description": "find me"},
            ]}
        }),
    ])
    filters = client_with(session)
    result = filters.search("find")
    assert [item.id for item in result] == [2]


def test_save_failure_does_not_succeed_silently():
    filters = client_with(Session([]))
    try:
        filters._require_success(Response(
            text="The filter edit form is still open",
            url="http://example.org/index.php/Special:AbuseFilter/1",
        ))
    except FilterSaveError as exc:
        assert "did not complete successfully" in str(exc)
    else:
        raise AssertionError("expected FilterSaveError")


def test_edit_form_response_can_be_a_success():
    filters = client_with(Session([]))
    filters._require_success(Response(
        text='<form id="mw-abusefilter-editing-form"><input name="wpEditToken" value="token"></form>',
        url="http://example.org/index.php/Special:AbuseFilter/1",
    ))


def test_redirect_response_can_be_a_success():
    filters = client_with(Session([]))
    filters._require_success(Response(
        text="Abuse filter management",
        url="http://example.org/index.php/Special:AbuseFilter",
        history=[Response(url="http://example.org/index.php/Special:AbuseFilter/1")],
    ))


def test_edit_normalizes_existing_rule_whitespace():
    session = Session([Response(text='<form><input name="wpEditToken" value="token"><textarea name="wpFilterRules">false \n</textarea></form>')])
    client = client_with(session)
    client._get_edit_form = lambda filter_id: (None, object(), {"wpFilterRules": "false \n"})
    client._apply_actions = lambda data, actions: None
    client._save_form = lambda form, data, response_url: Response(text='<form id="mw-abusefilter-editing-form"><input name="wpEditToken" value="token"></form>')
    client._require_success = lambda response: None
    client.refresh = None
    filter = Filter(client, 1, data={"wpFilterRules": "false"})
    result = filter.edit(append=" & true", dry_run=True)
    assert result["old_rules"] == "false"
    assert result["new_rules"] == "false & true"


def test_notes_append_and_replace_and_clear_without_whoami():
    session = Session([])
    client = client_with(session)
    client.whoami = lambda: (_ for _ in ()).throw(AssertionError("whoami should not be called"))
    client._get_edit_form = lambda filter_id: (None, object(), {
        "wpFilterRules": "false",
        "wpFilterNotes": "old note",
    })
    client._apply_actions = lambda data, actions: None
    client._preview = lambda filter_id, old_rules, data: data
    filter = Filter(client, 1, data={"wpFilterRules": "false", "wpFilterNotes": "old note"})
    assert filter.edit(notes="new note", sign_notes=True, dry_run=True)["wpFilterNotes"].startswith("old note\nnew note - DR ")
    assert filter.edit(notes="replacement", notes_mode="replace", dry_run=True)["wpFilterNotes"] == "replacement"
    assert filter.edit(notes="", notes_mode="replace", dry_run=True)["wpFilterNotes"] == ""



def test_edit_verifies_actions():
    session = Session([])
    client = client_with(session)
    filter = Filter(client, 1, data={"wpFilterRules": "false"})
    client._get_edit_form = lambda filter_id: (None, object(), {"wpFilterRules": "false"})
    client._apply_actions = lambda data, actions: data.update({"wpFilterActionWarn": "", "wpFilterWarnMessage": "abusefilter-warning"}) if actions else None
    client._save_form = lambda form, data, response_url: Response(text='<form id="mw-abusefilter-editing-form"></form>')
    client._require_success = lambda response: None
    saved = {}

    def refresh():
        filter._data.update(saved)
        return filter

    original_apply = client._apply_actions
    def apply(data, actions):
        original_apply(data, actions)
        saved.update(data)
    client._apply_actions = apply
    filter.refresh = refresh
    filter.edit(actions={"warn": "abusefilter-warning"})
    assert "warn" in filter.actions


def test_edit_action_verification_fails_on_mismatch():
    client = client_with(Session([]))
    filter = Filter(client, 1, data={"wpFilterRules": "false"})
    client._get_edit_form = lambda filter_id: (None, object(), {"wpFilterRules": "false"})
    client._apply_actions = lambda data, actions: data.update({"wpFilterActionWarn": "", "wpFilterWarnMessage": "abusefilter-warning"}) if actions else None
    client._save_form = lambda form, data, response_url: Response(text='<form id="mw-abusefilter-editing-form"></form>')
    client._require_success = lambda response: None
    filter.refresh = lambda: filter
    try:
        filter.edit(actions={"warn": "abusefilter-warning"})
    except FilterSaveError as exc:
        assert str(exc) == "actions verification failed"
    else:
        raise AssertionError("expected FilterSaveError")

def test_filter_permission_error_is_public():
    assert issubclass(FilterPermissionError, FilterSaveError)


def test_create_dry_run_does_not_post():
    assert inspect.signature(Filters.create).parameters["verify"].default is True
    assert inspect.signature(Filter.edit).parameters["verify"].default is True
    html = """<form action="/index.php/Special:AbuseFilter/new" method="post">
    <input name="wpEditToken" value="token">
    <input name="wpFilterEnabled" type="checkbox" value="" checked>
    </form>"""
    session = Session([Response(text=html)])
    filters = client_with(session)
    filters._article_path = "/index.php/$1"
    result = filters.create(
        "dry run",
        "false",
        notes="test",
        dry_run=True
    )
    assert result["filter_id"] is None
    assert result["description"] == "dry run"
    assert result["new_rules"] == "false"
    assert result["public"] is True
    assert len(session.calls) == 1
    assert session.calls[0][0] == "get"


def test_filters_debug_propagates_to_external_auth():
    session = Session([])
    auth = ExistingAuth()
    auth.session = session
    filters = Filters.__new__(Filters)
    filters.url = "http://example.org"
    filters.auth = auth
    filters.username = auth.username
    filters.password = auth.password
    filters.timeout = auth.timeout
    filters.tls_verify = auth.tls_verify
    filters.debug = False
    filters.session = session
    filters._article_path = None
    filters.__init__("http://example.org", auth=auth, debug=True)
    assert auth.debug is True
