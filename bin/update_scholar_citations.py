#!/usr/bin/env python3
"""One robots check and one public profile request, on macOS only.

No scholarly/browser/proxy/retry/detail-page/pagination code is used.
All parsing and validation precede any data change or Git write.
"""
import argparse
import copy
from datetime import datetime, timezone, date
import fcntl
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, ProxyHandler, HTTPRedirectHandler, build_opener

from bs4 import BeautifulSoup
import yaml

AUTHOR_ID = "cLfMY9wAAAAJ"
PROFILE_URL = "https://scholar.google.com/citations?user=" + AUTHOR_ID + "&hl=en"
ROBOTS_URL = "https://scholar.google.com/robots.txt"
USER_AGENT = "PersonalScholarUpdater/1.0"
OUTPUT = Path("_data/citations.yml")
MAX_BYTES = 2_000_000


class UpdateError(RuntimeError):
    pass


def integer(text):
    text = text.strip()
    if not re.fullmatch(r"(?:0|[1-9]\d*|[1-9]\d{0,2}(?:,\d{3})+)", text):
        raise UpdateError("Invalid integer: " + repr(text))
    value = int(text.replace(",", ""))
    if value > 1_000_000_000:
        raise UpdateError("Implausible integer")
    return value


def blocked_html(text):
    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.get_text(" ", strip=True).lower() if soup.title else ""
    return (
        bool(soup.select("#captcha, .g-recaptcha, #gs_captcha_f, form[action*='/sorry/'], iframe[src*='recaptcha']"))
        or any(x in title for x in ("captcha", "unusual traffic", "access denied", "sorry"))
        or "our systems have detected unusual traffic" in soup.get_text(" ", strip=True).lower()
    )


def robots_allows(text, url=PROFILE_URL):
    """RFC-style groups, wildcard/$ rules and longest-match Allow precedence.

    The request URL is fixed ASCII; unsupported/ambiguous robots documents fail closed.
    """
    if "<html" in text.lower() or len(text.encode("utf-8")) > 500_000:
        raise UpdateError("Invalid robots.txt")
    groups, agents, rules = [], [], []
    rules_started = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (x.strip() for x in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if rules_started:
                groups.append((agents, rules))
                agents, rules, rules_started = [], [], False
            if not value or not re.fullmatch(r"[\w*-]+", value):
                raise UpdateError("Invalid robots user-agent")
            agents.append(value.lower())
        elif key in ("allow", "disallow"):
            if not agents:
                raise UpdateError("Robots rule without user-agent")
            rules_started = True
            if value:
                if not value.startswith("/") or not value.isascii() or re.search(r"\s", value):
                    raise UpdateError("Unsupported robots rule")
                rules.append((key, value))
        elif key in ("crawl-delay", "request-rate") and agents:
            # No guesses about additional access restrictions.
            raise UpdateError("robots.txt specifies extra access restrictions")
    if agents:
        groups.append((agents, rules))
    if not groups:
        raise UpdateError("robots.txt has no valid user-agent groups")
    token = USER_AGENT.split("/")[0].lower()
    matching = []
    for names, entries in groups:
        specificity = max((len(n) for n in names if n != "*" and n in token), default=0)
        if specificity or "*" in names:
            matching.append((specificity, entries))
    if not matching:
        raise UpdateError("No applicable robots policy")
    priority = max(x[0] for x in matching)
    parsed = urlsplit(url)
    target = parsed.path + ("?" + parsed.query if parsed.query else "")
    matches = []
    for specificity, entries in matching:
        if specificity != priority:
            continue
        for kind, pattern in entries:
            anchored = pattern.endswith("$")
            core = pattern[:-1] if anchored else pattern
            expression = "^" + ".*".join(re.escape(p) for p in core.split("*"))
            if anchored:
                expression += "$"
            if re.search(expression, target):
                matches.append((len(core.replace("*", "")), kind == "allow"))
    return max(matches)[1] if matches else True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise UpdateError("Redirect refused; no additional URL requested")


def fetch(url, opener):
    if url not in (ROBOTS_URL, PROFILE_URL):
        raise UpdateError("URL outside the two-request allowlist")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain" if url == ROBOTS_URL else "text/html"})
    # One call only: urllib does not retry HTTP failures. No cookies or proxy settings.
    with opener.open(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != url:
            raise UpdateError("Unexpected HTTP status or URL")
        content_type = response.headers.get_content_type()
        allowed = ("text/plain",) if url == ROBOTS_URL else ("text/html",)
        if content_type not in allowed:
            raise UpdateError("Unexpected response Content-Type")
        limit = 500_000 if url == ROBOTS_URL else MAX_BYTES
        body = response.read(limit + 1)
        if len(body) > limit:
            raise UpdateError("Response too large")
        # Scholar may serve localized HTML in a declared legacy encoding.
        encoding = "utf-8-sig"
        if url == PROFILE_URL:
            encoding = response.headers.get_content_charset() or "utf-8"
        return body.decode(encoding, errors="strict")


def validate_saved(data):
    if not isinstance(data, dict) or not isinstance(data.get("metadata"), dict):
        raise UpdateError("Invalid existing metadata")
    papers = data.get("papers")
    if not isinstance(papers, dict) or not papers:
        raise UpdateError("Existing paper list is missing")
    for key, paper in papers.items():
        if not isinstance(key, str) or not re.fullmatch(r"(?:cLfMY9wAAAAJ:)?[\w-]+", key):
            raise UpdateError("Invalid stored paper ID")
        if not isinstance(paper, dict) or not isinstance(paper.get("title"), str) or not paper["title"].strip():
            raise UpdateError("Invalid stored title")
        if not isinstance(paper.get("year"), str):
            raise UpdateError("Invalid stored year")
        if type(paper.get("citations")) is not int or not 0 <= paper["citations"] <= 1_000_000_000:
            raise UpdateError("Invalid stored citation count")
    return data


def load_existing(repo):
    data = yaml.safe_load((repo / OUTPUT).read_text(encoding="utf-8"))
    return validate_saved(data)


def parse_profile(html, previous, now=None):
    validate_saved(previous)
    if blocked_html(html):
        raise UpdateError("CAPTCHA or blocking page detected")
    soup = BeautifulSoup(html, "html.parser")
    name_node = soup.select_one("#gsc_prf_in")
    if not name_node or not name_node.get_text(strip=True):
        raise UpdateError("Missing public profile identity")
    metric_rows = soup.select("#gsc_rsb_st tbody tr")
    labels = {"citations": "citations", "h-index": "h_index", "i10-index": "i10_index"}
    metrics = {}
    for row in metric_rows:
        label = row.select_one(".gsc_rsb_sc1")
        cells = row.select(".gsc_rsb_std")
        if label is None or len(cells) != 2:
            raise UpdateError("Unexpected summary metric row")
        key = labels.get(label.get_text(" ", strip=True).lower())
        if key is None or key in metrics:
            raise UpdateError("Unknown or duplicated metric")
        metrics[key] = {"all": integer(cells[0].get_text(strip=True)), "recent": integer(cells[1].get_text(strip=True))}
    if set(metrics) != set(labels.values()):
        raise UpdateError("Missing citation/h-index/i10-index metrics")
    headers = soup.select("#gsc_rsb_st thead th")
    if len(headers) != 3 or headers[1].get_text(strip=True) != "All":
        raise UpdateError("Unexpected summary metric headers")
    since = headers[2].get_text(" ", strip=True)
    if not re.fullmatch(r"Since \d{4}", since):
        raise UpdateError("Missing recent-period label")
    years = soup.select(".gsc_g_t")
    bars = soup.select(".gsc_g_al")
    if not years or len(years) != len(bars):
        raise UpdateError("Incomplete annual citation chart")
    annual = {}
    for year_node, count_node in zip(years, bars):
        year = year_node.get_text(strip=True)
        if not re.fullmatch(r"(?:19|20)\d{2}", year) or year in annual or int(year) > date.today().year:
            raise UpdateError("Invalid or duplicated chart year")
        annual[year] = integer(count_node.get_text(strip=True))

    visible = {}
    rows = soup.select("#gsc_a_b .gsc_a_tr")
    for row in rows:
        title_node = row.select_one("a.gsc_a_at")
        count_node = row.select_one(".gsc_a_c a.gsc_a_ac")
        year_node = row.select_one(".gsc_a_y")
        if title_node is None or count_node is None or year_node is None:
            raise UpdateError("Incomplete publication row")
        # Parse the link as data only; never follow it.
        link = urlsplit(title_node.get("href", ""))
        if link.path != "/citations" or link.netloc not in ("", "scholar.google.com"):
            raise UpdateError("Unexpected publication ID link")
        query = parse_qs(link.query)
        ids = query.get("citation_for_view", [])
        if len(ids) != 1 or not re.fullmatch(re.escape(AUTHOR_ID) + r":[\w-]+", ids[0]):
            raise UpdateError("Publication belongs to another profile or has no ID")
        paper_id = ids[0]
        if paper_id in visible:
            raise UpdateError("Duplicated publication ID")
        title = title_node.get_text(" ", strip=True)
        year = year_node.get_text(strip=True)
        if not title or (year and not re.fullmatch(r"(?:19|20)\d{2}", year)):
            raise UpdateError("Invalid title/year")
        count_text = count_node.get_text(strip=True)
        # Scholar represents uncited publications with an empty .gsc_a_ac anchor.
        citations = 0 if count_text == "" else integer(count_text)
        visible[paper_id] = {"title": title, "year": year, "citations": citations}
    minimum = min(len(previous["papers"]), 20)
    range_node = soup.select_one("#gsc_a_nn")
    if range_node is not None:
        page_range = re.fullmatch(r"(?:Articles\s+)?1\s*[–-]\s*(\d+)", range_node.get_text(" ", strip=True))
        if not page_range or int(page_range[1]) != len(visible):
            raise UpdateError("Displayed article range does not match the parsed rows")
        minimum = 1
    if not visible or len(visible) < minimum:
        raise UpdateError("Publication table is incomplete; old data retained")
    total = metrics["citations"]["all"]
    if sum(p["citations"] for p in visible.values()) > total or sum(annual.values()) > total:
        raise UpdateError("Citation totals contradict visible data")
    for scope in ("all", "recent"):
        if metrics["h_index"][scope] > metrics["citations"][scope] or 10 * metrics["i10_index"][scope] > metrics["citations"][scope]:
            raise UpdateError("Inconsistent index metrics")
    if any(v["recent"] > v["all"] for v in metrics.values()):
        raise UpdateError("Recent metrics exceed all-time metrics")
    if total == 0 and any(p["citations"] > 0 for p in previous["papers"].values()):
        raise UpdateError("Unexpected all-zero profile")
    result = copy.deepcopy(previous)
    stamp = now or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    # Preserve all existing papers and any fields not provided by the basic page.
    for paper_id, values in visible.items():
        short_id = paper_id.split(":", 1)[1]
        target = short_id if short_id in result["papers"] and paper_id not in result["papers"] else paper_id
        result["papers"].setdefault(target, {}).update(values)
    result["metadata"].update({
        "last_updated": stamp, "timezone": "UTC", "fetch_status": "success",
        "profile_url": PROFILE_URL, "source": "public_profile_html",
        "scope": "basic_profile_only", "observed_paper_ids": sorted(visible),
        "unobserved_papers": "preserved; counts may be older",
    })
    result["metadata"].pop("fetch_failed_at", None)
    result["metadata"].pop("fetch_error", None)
    result["profile"] = {"name": name_node.get_text(" ", strip=True), "user_id": AUTHOR_ID}
    result["metrics"] = metrics
    result["metrics"]["recent_label"] = since
    result["citations_by_year"] = annual
    return validate_saved(result)


def collect(previous, opener=None):
    opener = opener or build_opener(ProxyHandler({}), NoRedirect())
    robots = fetch(ROBOTS_URL, opener)
    if not robots_allows(robots):
        raise UpdateError("robots.txt does not allow the exact basic profile URL")
    html = fetch(PROFILE_URL, opener)
    return parse_profile(html, previous)


def git(repo, *args):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes -o ConnectTimeout=20"
    return subprocess.check_output(
        ["git", "-C", str(repo), *args], text=True, stderr=subprocess.STDOUT,
        env=env, timeout=120,
    ).strip()


def preflight(repo):
    if git(repo, "rev-parse", "--show-toplevel") != str(repo):
        raise UpdateError("Run from a repository root")
    if git(repo, "branch", "--show-current") != "main":
        raise UpdateError("A dedicated main-branch checkout is required")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise UpdateError("Working tree must be completely clean")
    remote = git(repo, "remote", "get-url", "--push", "origin")
    if remote not in (
        "https://github.com/systemreliability/systemreliability.github.io.git",
        "https://github.com/systemreliability/systemreliability.github.io",
        "git@github.com:systemreliability/systemreliability.github.io.git",
        "ssh://git@github.com/systemreliability/systemreliability.github.io.git",
    ):
        raise UpdateError("Unexpected push remote")
    if git(repo, "config", "--get", "user.name") == "" or git(repo, "config", "--get", "user.email") == "":
        raise UpdateError("Git author must be configured")
    git(repo, "fetch", "origin", "main")
    # Never merge/rebase, discard edits, or push unrelated local commits.
    if git(repo, "rev-parse", "HEAD") != git(repo, "rev-parse", "origin/main"):
        raise UpdateError("Checkout differs from origin/main; synchronize it manually first")
    return git(repo, "rev-parse", "HEAD")


def atomic_write(path, data):
    fd, temporary = tempfile.mkstemp(prefix=".scholar-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            yaml.safe_dump(data, stream, allow_unicode=True, sort_keys=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def publish(repo, data, expected_head):
    validate_saved(data)
    # Recheck after network/parsing work, before touching the working tree.
    if git(repo, "rev-parse", "HEAD") != expected_head or git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise UpdateError("Repository changed during collection")
    path = repo / OUTPUT
    existed = path.exists()
    old = path.read_bytes() if existed else None
    committed = False
    try:
        atomic_write(path, data)
        git(repo, "add", "--", str(OUTPUT))
        git(repo, "commit", "-m", "Update Scholar profile from validated macOS collection", "--", str(OUTPUT))
        committed = True
        git(repo, "push", "origin", "HEAD:main")
    except Exception:
        if not committed:
            git(repo, "reset", "--", str(OUTPUT))
            if existed:
                path.write_bytes(old)
            elif path.exists():
                path.unlink()
        # A failed push retains its one validated local commit for manual recovery.
        raise


def run(repo, publish_data=False):
    if sys.platform != "darwin" or os.environ.get("GITHUB_ACTIONS"):
        raise UpdateError("Live collection is allowed only on personal macOS, never GitHub Actions")
    repo = repo.resolve()
    state = Path.home() / "Library" / "Application Support" / "PersonalScholarUpdater"
    state.mkdir(parents=True, exist_ok=True)
    # One profile-wide lock/throttle even if multiple checkouts are used.
    with (state / (AUTHOR_ID + ".lock")).open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise UpdateError("Another collection is running") from exc
        head = preflight(repo)
        previous = load_existing(repo)
        attempt = state / (AUTHOR_ID + ".last-attempt")
        today = date.today().isoformat()
        if attempt.exists() and attempt.read_text().strip() == today:
            raise UpdateError("Already attempted today; no retry, including after a block")
        attempt.write_text(today + "\n")
        data = collect(previous)
        print("Validated profile metrics and", len(data["metadata"]["observed_paper_ids"]), "visible publications")
        if publish_data:
            publish(repo, data, head)
            print("Updated", OUTPUT, "and pushed its validated commit")
        else:
            print("Check only: data and Git unchanged; next live attempt is tomorrow")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--publish", action="store_true", help="Write validated YAML, commit and push")
    args = parser.parse_args()
    try:
        print(datetime.now(timezone.utc).isoformat(), "Starting basic-profile collection", flush=True)
        run(args.repo, args.publish)
    except Exception as exc:
        print(datetime.now(timezone.utc).isoformat(), "Scholar update stopped:", str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
