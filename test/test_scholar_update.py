"""Offline-only fixtures; no request to Google is made by this test suite."""
import copy
from email.message import Message
import importlib.util
import yaml
import os
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scholar_update", ROOT / "bin/update_scholar_citations.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)
HTML = (ROOT / "test/fixtures/scholar_profile.html").read_text()
ROBOTS = "User-agent: *\nDisallow: /citations?\nAllow: /citations?user=\nDisallow: /citations?*cstart=\nDisallow: /scholar\n"
PREVIOUS = {
    "metadata": {"last_updated": "2026-11-25 00:00:00"},
    "papers": {
        "cLfMY9wAAAAJ:paperA": {"title": "First paper", "year": "2021", "citations": 26},
        "cLfMY9wAAAAJ:paperB": {"title": "Second paper", "year": "2025", "citations": 0},
    },
}


class Response:
    status = 200

    def __init__(self, url, text):
        self.url = url
        self.body = text.encode()
        self.headers = Message()
        self.headers["Content-Type"] = "text/plain" if url == updater.ROBOTS_URL else "text/html"

    def geturl(self):
        return self.url

    def read(self, size):
        return self.body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Opener:
    def __init__(self, robots=ROBOTS, html=HTML, error_url=None, code=403):
        self.robots, self.html = robots, html
        self.error_url, self.code = error_url, code
        self.urls = []

    def open(self, req, timeout):
        self.urls.append(req.full_url)
        if req.full_url == self.error_url:
            raise HTTPError(req.full_url, self.code, "blocked", {}, None)
        return Response(req.full_url, self.robots if req.full_url == updater.ROBOTS_URL else self.html)


class ScholarTests(unittest.TestCase):
    def test_profile_metrics_and_legacy_shape(self):
        result = updater.parse_profile(HTML, PREVIOUS, "2026-11-27 09:10:00")
        self.assertEqual(1234, result["metrics"]["citations"]["all"])
        self.assertEqual(10, result["metrics"]["h_index"]["all"])
        self.assertEqual(12, result["metrics"]["i10_index"]["all"])
        self.assertEqual({"2024": 40, "2025": 60}, result["citations_by_year"])
        self.assertEqual(27, result["papers"]["cLfMY9wAAAAJ:paperA"]["citations"])
        self.assertEqual(0, result["papers"]["cLfMY9wAAAAJ:paperB"]["citations"])
        self.assertEqual(26, PREVIOUS["papers"]["cLfMY9wAAAAJ:paperA"]["citations"])

    def test_retains_papers_not_visible_on_first_page(self):
        old = copy.deepcopy(PREVIOUS)
        old["papers"]["cLfMY9wAAAAJ:older"] = {"title": "Older", "year": "2000", "citations": 7}
        # Use 20 visible rows to model a first page with additional older papers.
        expanded = re.sub(r"</tbody>\s*</table>\s*<button", lambda match: "".join(
            '<tr class="gsc_a_tr"><td><a class="gsc_a_at" href="/citations?citation_for_view=cLfMY9wAAAAJ:extra' + str(i) +
            '">Extra</a></td><td class="gsc_a_c"><a class="gsc_a_ac"></a></td><td class="gsc_a_y">2025</td></tr>'
            for i in range(18)
        ) + match.group(0), HTML)
        result = updater.parse_profile(expanded, old)
        self.assertEqual(old["papers"]["cLfMY9wAAAAJ:older"], result["papers"]["cLfMY9wAAAAJ:older"])

    def test_smaller_complete_profile_preserves_old_papers(self):
        previous = copy.deepcopy(PREVIOUS)
        previous["papers"]["cLfMY9wAAAAJ:older"] = {"title": "Archived", "year": "2000", "citations": 1}
        html = HTML.replace("</body>", '<span id="gsc_a_nn">Articles 1–2</span></body>')
        result = updater.parse_profile(html, previous)
        self.assertEqual(3, len(result["papers"]))
        self.assertEqual(2, len(result["metadata"]["observed_paper_ids"]))
        with self.assertRaises(updater.UpdateError):
            updater.parse_profile(html.replace("1–2", "1–3"), previous)

    def test_exact_two_requests_no_following_links(self):
        opener = Opener()
        updater.collect(PREVIOUS, opener)
        self.assertEqual([updater.ROBOTS_URL, updater.PROFILE_URL], opener.urls)

    def test_disallowed_robots_never_fetch_profile(self):
        opener = Opener(robots="User-agent: *\nDisallow: /\n")
        with self.assertRaises(updater.UpdateError):
            updater.collect(PREVIOUS, opener)
        self.assertEqual([updater.ROBOTS_URL], opener.urls)

    def test_robots_longest_match_and_specific_agent(self):
        self.assertTrue(updater.robots_allows(ROBOTS))
        self.assertFalse(updater.robots_allows(ROBOTS, updater.PROFILE_URL + "&cstart=20"))
        self.assertFalse(updater.robots_allows(ROBOTS + "\nUser-agent: PersonalScholarUpdater\nDisallow: /\n"))
        self.assertTrue(updater.robots_allows("User-agent: *\nDisallow: /citations\nAllow: /citations?user=*\n"))
        with self.assertRaises(updater.UpdateError):
            updater.robots_allows("<html>Access denied</html>")

    def test_status_errors_stop_immediately(self):
        for url in (updater.ROBOTS_URL, updater.PROFILE_URL):
            for code in (403, 429, 500):
                with self.subTest(url=url, code=code):
                    opener = Opener(error_url=url, code=code)
                    with self.assertRaises(HTTPError):
                        updater.collect(PREVIOUS, opener)
                    self.assertEqual(1 if url == updater.ROBOTS_URL else 2, len(opener.urls))

    def test_redirect_never_followed(self):
        with self.assertRaises(updater.UpdateError):
            updater.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.org")
        opener = Opener()
        with self.assertRaises(updater.UpdateError):
            updater.fetch("https://scholar.google.com/scholar?q=x", opener)
        self.assertEqual([], opener.urls)

    def test_captcha_and_partial_html_rejected(self):
        for html in (
            '<title>Sorry</title><form action="/sorry/index"></form>',
            HTML.replace('<div id="gsc_prf_in">', '<div>'),
            HTML.replace('class="gsc_g_al"', 'class="missing"'),
            HTML.replace('class="gsc_a_ac"', 'class="missing"'),
            HTML.replace("cLfMY9wAAAAJ:paperA", "OTHER:paperA"),
            HTML.replace('>27</a>', '>N/A</a>'),
            HTML.replace('>1,234</td>', '>0</td>'),
            HTML.replace('class="gsc_a_tr"', 'class="missing"'),
        ):
            with self.subTest(html=html[:60]), self.assertRaises(updater.UpdateError):
                updater.parse_profile(html, PREVIOUS)

    def test_failure_keeps_files_and_never_publishes(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            (repo / "_data").mkdir(parents=True)
            target = repo / updater.OUTPUT
            target.write_text(yaml.safe_dump(PREVIOUS))
            original = target.read_bytes()
            with patch.object(updater.sys, "platform", "darwin"), patch.dict(os.environ, {}, clear=True), \
                 patch.object(updater.Path, "home", return_value=Path(temporary)), \
                 patch.object(updater, "preflight", return_value="HEAD"), \
                 patch.object(updater, "collect", side_effect=updater.UpdateError("blocked")), \
                 patch.object(updater, "publish") as publish:
                with self.assertRaises(updater.UpdateError):
                    updater.run(repo, True)
                self.assertEqual(original, target.read_bytes())
                publish.assert_not_called()
                # A second invocation on the same day cannot retry the network.
                with patch.object(updater, "collect") as collect:
                    with self.assertRaises(updater.UpdateError):
                        updater.run(repo, True)
                    collect.assert_not_called()

    def test_github_actions_never_collects(self):
        with patch.object(updater.sys, "platform", "darwin"), patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}), \
             patch.object(updater, "collect") as collect:
            with self.assertRaises(updater.UpdateError):
                updater.run(ROOT, True)
            collect.assert_not_called()

    def test_commit_failure_restores_previous_yaml(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "_data").mkdir()
            target = repo / updater.OUTPUT
            target.write_text(yaml.safe_dump(PREVIOUS))
            original = target.read_bytes()

            def fake_git(repo, *args):
                if args[0] == "rev-parse":
                    return "HEAD"
                if args[0] == "commit":
                    raise updater.UpdateError("commit failed")
                return ""
            with patch.object(updater, "git", side_effect=fake_git) as git:
                with self.assertRaises(updater.UpdateError):
                    updater.publish(repo, updater.parse_profile(HTML, PREVIOUS), "HEAD")
                self.assertEqual(original, target.read_bytes())
                self.assertFalse(any(c.args[1] == "push" for c in git.call_args_list))

    def test_push_failure_retains_validated_commit_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            (repo / "_data").mkdir()

            def fake_git(repo, *args):
                if args[0] == "rev-parse":
                    return "HEAD"
                if args[0] == "push":
                    raise updater.UpdateError("push failed")
                return ""
            result = updater.parse_profile(HTML, PREVIOUS)
            with patch.object(updater, "git", side_effect=fake_git):
                with self.assertRaises(updater.UpdateError):
                    updater.publish(repo, result, "HEAD")
            self.assertEqual(result, yaml.safe_load((repo / updater.OUTPUT).read_text()))

    def test_existing_real_yaml_is_accepted(self):
        data = updater.load_existing(ROOT)
        self.assertGreaterEqual(len(data["papers"]), 12)


if __name__ == "__main__":
    unittest.main()
