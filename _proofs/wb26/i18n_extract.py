"""Pass 9: pull every visible English string (text + alt/aria-label/title/placeholder + <title> and
meta description) out of a page. Shared by i18n_strings.py (dictionary build) and the UAT crawler."""
import re
from bs4 import BeautifulSoup, NavigableString, Comment
SKIP = {"script", "style", "noscript", "svg", "template", "code", "pre"}
ATTRS = ("alt", "aria-label", "title", "placeholder")
WS = re.compile(r"\s+")


def norm(s):
    return WS.sub(" ", s).strip()


def wanted(t):
    return len(t) > 1 and re.search(r"[A-Za-z]{2}", t) and not re.fullmatch(r"[\W\d_]*", t)


def strings(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    t = soup.find("title")
    if t and t.string:
        out.append(norm(t.string))
    for m in soup.find_all("meta"):
        if m.get("name") in ("description", "twitter:title", "twitter:description") or m.get("property") in ("og:title", "og:description"):
            if m.get("content"):
                out.append(norm(m["content"]))
    body = soup.body or soup
    for node in body.descendants:
        if isinstance(node, Comment):
            continue
        if isinstance(node, NavigableString):
            p = node.parent
            if p is None or any(a.name in SKIP for a in [p] + list(p.parents) if a.name):
                continue
            if any(a.get("translate") == "no" for a in [p] + list(p.parents) if hasattr(a, "get") and a.name):
                continue
            s = norm(str(node))
            if wanted(s):
                out.append(s)
        elif getattr(node, "attrs", None):
            if node.name in SKIP:
                continue
            for a in ATTRS:
                v = node.attrs.get(a)
                if isinstance(v, str) and wanted(norm(v)):
                    out.append(norm(v))
    return out
