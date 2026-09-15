from mediawiki_abusefilter.forms import parse_form


def test_form_parser_handles_empty_checkbox_values():
    html = '''
    <form action="/index.php" method="post">
      <input name="wpEditToken" value="token">
      <input name="enabled" type="checkbox" value="" checked>
      <input name="disabled" type="checkbox" value="" disabled checked>
      <select name="message"><option value="one">one</option><option selected value="two">two</option></select>
      <textarea name="rules">false\n</textarea>
    </form>
    '''
    _, _, data = parse_form(html)
    assert data["wpEditToken"] == "token"
    assert data["enabled"] == ""
    assert "disabled" not in data
    assert data["message"] == "two"
    assert data["rules"] == "false\n"
