"""Checks on the Jekyll site configuration and, when it has been built,
on the links in the generated HTML.

The site is deployed to GitHub *project* Pages at
https://labordynamicsinstitute.github.io/stata-ssc2/, i.e. under a path
prefix rather than at the host root. Jekyll only emits that prefix when
`baseurl` is set; without it every `{{ site.baseurl }}`-derived link --
including the theme's stylesheets -- points at the host root and 404s,
which renders the site completely unstyled.

Standard library only, matching the rest of this repository's Python.
The built-output checks are skipped when site/_site is absent, so the
module still passes on a clean checkout (site/_site is gitignored);
tools/serve_site.sh builds it.
"""

import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
CONFIG = REPO / "site" / "_config.yml"
BUILT = REPO / "site" / "_site"

# Where GitHub publishes this repository's Pages site, and the path
# prefix that follows from it.
DEPLOY_URL = "https://labordynamicsinstitute.github.io/stata-ssc2"
BASEURL = "/stata-ssc2"

# Top-level `key: value` in _config.yml, ignoring nested/list entries.
_TOP_LEVEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)[ \t]*$")

# href="..." / src="..." in the generated HTML.
_LINK = re.compile(r'(?:href|src)="([^"]*)"')


def read_config():
    """Return the top-level scalar keys of _config.yml as a dict of strings."""
    values = {}
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        match = _TOP_LEVEL.match(line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return values


class BaseUrlConfigTest(unittest.TestCase):
    def setUp(self):
        self.config = read_config()

    def test_url_is_the_origin_only(self):
        """`url` is the origin; the path prefix belongs in `baseurl`."""
        self.assertIn("url", self.config, "_config.yml must set url")
        self.assertEqual(
            urlparse(self.config["url"]).path.rstrip("/"),
            "",
            "url must carry no path -- Jekyll takes the path prefix from "
            "baseurl, and a path smuggled into url is silently ignored when "
            "building asset links",
        )

    def test_baseurl_is_the_project_pages_prefix(self):
        self.assertEqual(
            self.config.get("baseurl", ""),
            BASEURL,
            "baseurl must be %r, otherwise Jekyll emits root-absolute asset "
            "links that 404 on GitHub project Pages" % BASEURL,
        )

    def test_url_and_baseurl_reconstruct_the_deployment_url(self):
        self.assertEqual(
            self.config["url"].rstrip("/") + self.config.get("baseurl", ""),
            DEPLOY_URL,
            "url + baseurl must equal the address the site is published at",
        )


class BuiltLinkTest(unittest.TestCase):
    """Every root-absolute link in the built HTML must carry the prefix."""

    def setUp(self):
        if not BUILT.is_dir():
            self.skipTest("site/_site not built; run tools/serve_site.sh build")
        self.pages = sorted(BUILT.rglob("*.html"))
        if not self.pages:
            self.skipTest("site/_site contains no HTML")
        self.baseurl = read_config().get("baseurl", "")

    def test_root_absolute_links_are_prefixed(self):
        offenders = []
        for page in self.pages:
            for link in _LINK.findall(page.read_text(encoding="utf-8")):
                # Only site-root-absolute links can lose the prefix;
                # protocol-relative (//), fragment, and relative links cannot.
                if not link.startswith("/") or link.startswith("//"):
                    continue
                if link == self.baseurl or link.startswith(self.baseurl + "/"):
                    continue
                offenders.append("%s: %s" % (page.relative_to(BUILT), link))
        self.assertEqual(
            [],
            offenders,
            "links missing the %r prefix will 404 on GitHub project Pages:\n%s"
            % (self.baseurl, "\n".join(offenders)),
        )

    def test_theme_stylesheet_is_linked_and_present(self):
        """The symptom that started this: the theme CSS must resolve on disk."""
        index = BUILT / "index.html"
        self.assertTrue(index.is_file(), "site/_site/index.html not built")
        html = index.read_text(encoding="utf-8")
        sheets = [
            link
            for link in _LINK.findall(html)
            if link.startswith("/") and link.endswith(".css")
        ]
        self.assertTrue(sheets, "index.html links no stylesheet")
        for sheet in sheets:
            relative = sheet[len(self.baseurl) :].lstrip("/")
            self.assertTrue(
                (BUILT / relative).is_file(),
                "index.html links %s but %s was not generated" % (sheet, relative),
            )


class ExternalPickerScriptTest(unittest.TestCase):
    """The picker script must stay in an external asset, never inline.

    just-the-docs pipes every page through jekyll-compress-html, whose
    whitespace-collapse step rewrites all whitespace runs outside <pre>
    into single spaces -- inline <script> contents included. A flattened
    script dies at its first `//` comment, which killed the whole
    deployed picker once (v2.2.2 era). Static assets are copied verbatim
    by Jekyll and are immune, so the script lives in
    site/assets/js/picker.js and is loaded from the theme's custom-head
    include, gated to pages that set `picker: true` front matter.
    """

    SITE = REPO / "site"
    PICKER = SITE / "assets" / "js" / "picker.js"
    HEAD = SITE / "_includes" / "head_custom.html"
    _INLINE = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>\s*\S", re.S)

    def test_site_pages_have_no_inline_scripts(self):
        offenders = [
            str(page.relative_to(REPO))
            for page in list(self.SITE.glob("*.html")) + list(self.SITE.glob("*.md"))
            if self._INLINE.search(page.read_text(encoding="utf-8"))
        ]
        self.assertEqual(
            [],
            offenders,
            "inline <script> content is corrupted by the theme's HTML "
            "compression; move it to site/assets/ and load it via "
            "_includes/head_custom.html:\n" + "\n".join(offenders),
        )

    def test_picker_script_asset_exists_with_data_markers(self):
        self.assertTrue(self.PICKER.is_file(), "site/assets/js/picker.js missing")
        js = self.PICKER.read_text(encoding="utf-8")
        for marker in ("@@DATA-START@@", "@@DATA-END@@"):
            self.assertIn(
                marker,
                js,
                "picker.js must keep the %s marker that site/build_data.py "
                "rewrites in CI" % marker,
            )

    def test_head_custom_loads_picker_behind_front_matter_gate(self):
        self.assertTrue(
            self.HEAD.is_file(), "site/_includes/head_custom.html missing"
        )
        head = self.HEAD.read_text(encoding="utf-8")
        self.assertIn(
            "{% if page.picker %}",
            head,
            "the picker script must load only on pages opting in via "
            "`picker: true`; it dereferences picker-only elements and "
            "would throw on every other page",
        )
        self.assertRegex(
            head,
            r"relative_url",
            "the script src must go through relative_url so it carries "
            "the baseurl prefix on project Pages",
        )
        self.assertRegex(
            head,
            r"<script[^>]*\bdefer\b",
            "the script must load with defer: it wires the DOM at top "
            "level and, loaded from <head> without defer, would run "
            "before the body exists",
        )

    def test_index_front_matter_opts_into_picker(self):
        index = (self.SITE / "index.html").read_text(encoding="utf-8")
        front = index.split("---")[1]
        self.assertRegex(
            front,
            r"(?m)^picker: true$",
            "site/index.html must set `picker: true` or the custom-head "
            "gate never loads the picker script",
        )


class BuiltPickerScriptTest(unittest.TestCase):
    """When the site has been built, index.html must actually load the
    picker asset and the asset must exist in the output. Skipped on a
    clean checkout, like the other built-output checks."""

    def setUp(self):
        if not BUILT.is_dir():
            self.skipTest("site/_site not built; run tools/serve_site.sh")
        self.baseurl = read_config().get("baseurl", "")

    def test_built_index_links_existing_picker_script(self):
        html = (BUILT / "index.html").read_text(encoding="utf-8")
        scripts = [
            link
            for link in _LINK.findall(html)
            if link.endswith("/assets/js/picker.js")
        ]
        self.assertTrue(scripts, "built index.html does not load picker.js")
        for src in scripts:
            self.assertTrue(
                src.startswith(self.baseurl + "/"),
                "picker.js src %r lacks the %r prefix" % (src, self.baseurl),
            )
            relative = src[len(self.baseurl) :].lstrip("/")
            self.assertTrue(
                (BUILT / relative).is_file(),
                "index.html loads %s but %s was not generated" % (src, relative),
            )


if __name__ == "__main__":
    unittest.main()
