from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .exceptions import FilterError


def parse_form(html):
    soup = BeautifulSoup(html, "html.parser")
    token = soup.select_one('input[name="wpEditToken"]')
    if not token:
        raise FilterError("wpEditToken not found")
    form = token.find_parent("form")
    if not form:
        raise FilterError("AbuseFilter form not found")
    # keep values we don't explicitly change later
    data = {}
    for element in form.select("input, textarea, select"):
        name = element.get("name")
        if not name or element.has_attr("disabled"):
            continue
        element_type = element.get("type")
        if element.name == "select":
            selected = element.select_one("option[selected]") or element.find("option")
            data[name] = selected.get("value", "") if selected else ""
        elif element_type in {"checkbox", "radio"}:
            if element.has_attr("checked"):
                data[name] = element.get("value", "")
        elif element.name == "textarea":
            data[name] = element.text
        elif element_type not in {"submit", "button", "reset", "file", "image"}:
            data[name] = element.get("value", "")
    return soup, form, data


def form_action(page_url, form):
    return urljoin(page_url, form.get("action", ""))
