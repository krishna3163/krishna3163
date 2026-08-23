"""Automated Profile README & Stats Generator for krishna3163.

Updates:
1. Live LeetCode Stats
2. Recent GitHub Activity Stream
3. Top Repositories & Live Star Showcase
4. Daily Programming Quote & Joke
5. Resume (CV.pdf) Metadata & Download Link
6. Dynamic Greeting & Profile Status
7. Tech Articles & Insights Showcase
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("profile-updater")

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
CV_PATH = ROOT / "CV.pdf"

GITHUB_USERNAME = "krishna3163"
LEETCODE_USERNAME = "krishna0858"

# ---------------------------------------------------------------------------
# 1. LeetCode Stats Fetcher
# ---------------------------------------------------------------------------


def fetch_leetcode_stats(username: str = LEETCODE_USERNAME) -> dict:
    """Fetch live LeetCode stats via GraphQL API."""
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile {
          ranking
          reputation
        }
        submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://leetcode.com/graphql",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            matched = data.get("data", {}).get("matchedUser")
            if not matched:
                return {}

            sub_stats = matched.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
            stats = {item["difficulty"]: item["count"] for item in sub_stats}
            ranking = matched.get("profile", {}).get("ranking", 0)

            return {
                "total": stats.get("All", 0),
                "easy": stats.get("Easy", 0),
                "medium": stats.get("Medium", 0),
                "hard": stats.get("Hard", 0),
                "ranking": f"{ranking:,}" if ranking else "Top Tier",
            }
    except Exception as exc:
        logger.warning("[WARNING] Failed to fetch LeetCode stats: %s", exc)
        return {}


def generate_leetcode_section(stats: dict) -> str:
    """Generate markdown block for LeetCode stats."""
    if not stats:
        # Fallback card
        return (
            '<div align="center">\n'
            f'  <a href="https://leetcode.com/u/{LEETCODE_USERNAME}/" target="_blank">\n'
            f'    <img src="https://leetcode-stats.vercel.app/api?username={LEETCODE_USERNAME}&theme=Dark" alt="LeetCode Stats" width="85%" />\n'
            '  </a>\n'
            '</div>'
        )

    total = stats.get("total", 0)
    easy = stats.get("easy", 0)
    medium = stats.get("medium", 0)
    hard = stats.get("hard", 0)
    ranking = stats.get("ranking", "N/A")

    return (
        '<div align="center">\n'
        '  <table width="100%">\n'
        '    <tr>\n'
        '      <td width="35%" align="center" valign="middle">\n'
        f'        <a href="https://leetcode.com/u/{LEETCODE_USERNAME}/" target="_blank">\n'
        '          <img src="https://img.shields.io/badge/LeetCode-Profile-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" />\n'
        '        </a>\n'
        f'        <h3><b>🧩 {total} Problems Solved</b></h3>\n'
        f'        <p>🏆 <b>Global Rank:</b> <code>#{ranking}</code></p>\n'
        '      </td>\n'
        '      <td width="65%" valign="middle">\n'
        f'        <p>🟢 <b>Easy:</b> <code>{easy}</code> solved</p>\n'
        f'        <p>🟡 <b>Medium:</b> <code>{medium}</code> solved</p>\n'
        f'        <p>🔴 <b>Hard:</b> <code>{hard}</code> solved</p>\n'
        '      </td>\n'
        '    </tr>\n'
        '  </table>\n'
        '</div>'
    )


# ---------------------------------------------------------------------------
# 2. Recent GitHub Activity Stream Fetcher
# ---------------------------------------------------------------------------


def fetch_recent_activity(username: str = GITHUB_USERNAME, limit: int = 5) -> list[dict]:
    """Fetch and deduplicate public activity events for the user."""
    url = f"https://api.github.com/users/{username}/events/public?per_page=40"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    activities: list[dict] = []
    seen_keys: set[str] = set()

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            events = json.loads(resp.read().decode("utf-8"))

            for event in events:
                if len(activities) >= limit:
                    break

                etype = event.get("type")
                repo_name = event.get("repo", {}).get("name", "")
                repo_url = f"https://github.com/{repo_name}"
                created_at = event.get("created_at", "")
                date_str = created_at[:10] if created_at else ""

                if etype == "PushEvent":
                    payload = event.get("payload", {})
                    commits = payload.get("commits", [])
                    count = payload.get("size") or payload.get("distinct_size") or len(commits) or 1
                    msg = commits[0].get("message", "").split("\n")[0] if commits else "Update codebase"
                    if len(msg) > 55:
                        msg = msg[:52] + "..."

                    key = f"push:{repo_name}:{date_str}"
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    activities.append({
                        "icon": "🔨",
                        "action": f"Pushed <b>{count} commit(s)</b>",
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "detail": msg,
                        "date": date_str,
                    })

                elif etype == "CreateEvent":
                    ref_type = event.get("payload", {}).get("ref_type", "branch")
                    key = f"create:{repo_name}:{ref_type}:{date_str}"
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    activities.append({
                        "icon": "✨",
                        "action": f"Created {ref_type}",
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "detail": f"New {ref_type} initialized",
                        "date": date_str,
                    })

                elif etype == "WatchEvent":
                    key = f"watch:{repo_name}"
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    activities.append({
                        "icon": "⭐",
                        "action": "Starred repo",
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "detail": "Saved to favorites",
                        "date": date_str,
                    })

                elif etype == "PullRequestEvent":
                    action = event.get("payload", {}).get("action", "opened")
                    pr_num = event.get("payload", {}).get("number", "")
                    activities.append({
                        "icon": "🔀",
                        "action": f"{action.capitalize()} PR #{pr_num}",
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "detail": "Pull request contribution",
                        "date": date_str,
                    })

                elif etype == "ReleaseEvent":
                    tag = event.get("payload", {}).get("release", {}).get("tag_name", "release")
                    activities.append({
                        "icon": "🚀",
                        "action": f"Release <b>{tag}</b>",
                        "repo_name": repo_name,
                        "repo_url": repo_url,
                        "detail": f"Published release {tag}",
                        "date": date_str,
                    })

    except Exception as exc:
        logger.warning("[WARNING] Failed to fetch GitHub activity: %s", exc)

    return activities


def generate_recent_activity_section(activities: list[dict]) -> str:
    """Generate sleek, modern table card for recent activity stream."""
    if not activities:
        return (
            '<div align="center">\n'
            '  <p>🚀 <i>Active daily in open-source development and algorithm problem-solving.</i></p>\n'
            '</div>'
        )

    lines = []
    lines.append('<div align="center">')
    lines.append('  <table width="100%">')
    lines.append('    <tr>')
    lines.append('      <th align="left" width="22%">Activity</th>')
    lines.append('      <th align="left" width="40%">Repository</th>')
    lines.append('      <th align="left" width="26%">Summary</th>')
    lines.append('      <th align="center" width="12%">Date</th>')
    lines.append('    </tr>')

    for act in activities:
        icon = act["icon"]
        action = act["action"]
        repo_name = act["repo_name"]
        repo_url = act["repo_url"]
        detail = act["detail"]
        date = act["date"]

        lines.append('    <tr>')
        lines.append(f'      <td align="left">{icon} {action}</td>')
        lines.append(f'      <td align="left"><a href="{repo_url}"><code>{repo_name}</code></a></td>')
        lines.append(f'      <td align="left"><i>{detail}</i></td>')
        lines.append(f'      <td align="center"><code>{date}</code></td>')
        lines.append('    </tr>')

    lines.append('  </table>')
    lines.append('</div>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. Community Wall: Stargazers & Followers Showcase
# ---------------------------------------------------------------------------


def fetch_stargazers(username: str = GITHUB_USERNAME, limit: int = 40) -> list[dict]:
    """Fetch stargazers across user's public repositories."""
    stargazers: dict[str, dict] = {}
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3.star+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos = [
        "best_shizuku_apps_for_android_no_root",
        "awesome-android-app-repositories",
        "OpenDiscover",
        "GooglePhoto_Alternative",
        "best-root-apps-for-android",
        "krishna3163",
    ]

    for repo in repos:
        try:
            url = f"https://api.github.com/repos/{username}/{repo}/stargazers?per_page=30"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for s in data:
                    user_data = s.get("user", s) if isinstance(s, dict) else {}
                    login = user_data.get("login")
                    avatar = user_data.get("avatar_url", f"https://github.com/{login}.png")
                    if login and login not in stargazers and login != username:
                        stargazers[login] = {
                            "login": login,
                            "avatar_url": avatar,
                            "url": f"https://github.com/{login}",
                            "repo": repo,
                        }
        except Exception as exc:
            logger.warning("[WARNING] Failed to fetch stargazers for %s: %s", repo, exc)

    return list(stargazers.values())[:limit]


def fetch_followers(username: str = GITHUB_USERNAME, limit: int = 40) -> list[dict]:
    """Fetch public followers."""
    followers: list[dict] = []
    headers = {"User-Agent": "Mozilla/5.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        url = f"https://api.github.com/users/{username}/followers?per_page=50"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for u in data:
                login = u.get("login")
                if login:
                    followers.append({
                        "login": login,
                        "avatar_url": u.get("avatar_url", f"https://github.com/{login}.png"),
                        "url": u.get("html_url", f"https://github.com/{login}"),
                    })
    except Exception as exc:
        logger.warning("[WARNING] Failed to fetch followers: %s", exc)

    return followers[:limit]


def generate_community_wall_section(stargazers: list[dict], followers: list[dict]) -> str:
    """Generate compact interactive avatar walls for Stargazers and Followers."""
    lines = []
    lines.append('<div align="center">')
    lines.append('  <p>💖 <b>A heartfelt thank you to everyone who stars my repositories, follows my journey, and supports open source!</b></p>')
    lines.append('  <br>')

    # 1. Stargazers Wall (Gold Border)
    if stargazers:
        lines.append(f'  <h4><b>⭐ Stargazers Wall of Fame ({len(stargazers)}+ Supporters)</b></h4>')
        lines.append('  <p>')
        for s in stargazers:
            login = s["login"]
            avatar = s["avatar_url"]
            url = s["url"]
            repo = s.get("repo", "projects")
            lines.append(f'    <a href="{url}" target="_blank" title="⭐ @{login} starred {repo}">\n      <img src="{avatar}" width="36" height="36" style="border-radius: 50%; margin: 2px; border: 1.5px solid #FFA116;" alt="@{login}" />\n    </a>')
        lines.append('  </p>')
        lines.append('  <br>')

    # 2. Followers Wall (Purple Border - Medium Size)
    if followers:
        lines.append(f'  <h4><b>👥 Community Followers ({len(followers)}+ Developers)</b></h4>')
        lines.append('  <p>')
        for f in followers:
            login = f["login"]
            avatar = f["avatar_url"]
            url = f["url"]
            lines.append(f'    <a href="{url}" target="_blank" title="👥 Follower @{login}">\n      <img src="{avatar}" width="50" height="50" style="border-radius: 50%; margin: 3px; border: 2px solid #8B5CF6;" alt="@{login}" />\n    </a>')
        lines.append('  </p>')
        lines.append('  <br>')

    lines.append('  <p><sub>⭐ <i>Star any of my repositories or hit follow to be automatically featured on this wall!</i></sub></p>')
    lines.append('</div>')

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. Top Repositories & Star Count Showcase
# ---------------------------------------------------------------------------


def fetch_top_repositories(username: str = GITHUB_USERNAME) -> list[dict]:
    """Fetch user's public repositories and sort by star count and activity."""
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    repos = []
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for r in data:
                if r.get("fork"):
                    continue
                name = r.get("name", "")
                if name.lower() == username.lower():
                    continue
                repos.append({
                    "name": name,
                    "url": r.get("html_url", ""),
                    "description": r.get("description") or "Open source project by Krishna Kumar",
                    "stars": r.get("stargazers_count", 0),
                    "forks": r.get("forks_count", 0),
                    "language": r.get("language") or "Python / Java",
                })
    except Exception as exc:
        logger.warning("[WARNING] Failed to fetch repositories: %s", exc)

    # Sort by stars then recency
    repos.sort(key=lambda x: x["stars"], reverse=True)
    return repos[:4]


def generate_top_repos_section(repos: list[dict]) -> str:
    """Generate top repositories showcase table."""
    if not repos:
        return ""

    lines = []
    lines.append('<div align="center">')
    lines.append('  <table width="100%">')

    for i in range(0, len(repos), 2):
        lines.append('    <tr>')
        for j in range(2):
            if i + j < len(repos):
                r = repos[i + j]
                name = r["name"]
                url = r["url"]
                desc = r["description"]
                if len(desc) > 85:
                    desc = desc[:82] + "..."
                stars = r["stars"]
                forks = r["forks"]
                lang = r["language"]

                lines.append('      <td width="50%" valign="top">')
                lines.append(f'        <h4><a href="{url}">📦 {name}</a></h4>')
                lines.append(f'        <p>{desc}</p>')
                lines.append(f'        <p>⭐ <b>{stars}</b> &nbsp;|&nbsp; 🍴 <b>{forks}</b> &nbsp;|&nbsp; 🏷️ <code>{lang}</code></p>')
                lines.append('      </td>')
        lines.append('    </tr>')

    lines.append('  </table>')
    lines.append('</div>')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 4. Daily Tech Quotes & Jokes Pool
# ---------------------------------------------------------------------------

QUOTES_AND_JOKES = [
    ("“Any fool can write code that a computer can understand. Good programmers write code that humans can understand.”", "Martin Fowler"),
    ("“First, solve the problem. Then, write the code.”", "John Johnson"),
    ("“Experience is the name everyone gives to their mistakes.”", "Oscar Wilde"),
    ("“Java is to JavaScript what car is to Carpet.”", "Chris Heilmann"),
    ("“Knowledge is power, but enthusiasm pulls the switch.”", "Ivern Ball"),
    ("“Simplicity is prerequisite for reliability.”", "Edsger W. Dijkstra"),
    ("“Talk is cheap. Show me the code.”", "Linus Torvalds"),
    ("“Software is like entropy: It is difficult to grasp, weighs nothing, and obeys the Second Law of Thermodynamics.”", "Norman Ralph Augustine"),
    ("“Fix the cause, not the symptom.”", "Steve Maguire"),
    ("“Before software can be reusable it first has to be usable.”", "Ralph Johnson"),
    ("“There are only two hard things in Computer Science: cache invalidation and naming things.”", "Phil Karlton"),
    ("“Walking on water and developing software from a specification are easy if both are frozen.”", "Edward V. Berard"),
]


def get_daily_quote() -> str:
    """Return a quote based on the current day of the year."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    quote, author = QUOTES_AND_JOKES[day_of_year % len(QUOTES_AND_JOKES)]
    return f"> *{quote}* — **{author}**"


# ---------------------------------------------------------------------------
# 5. Resume (CV.pdf) Metadata & Info
# ---------------------------------------------------------------------------


def get_resume_info() -> str:
    """Read CV.pdf and generate dynamic download metadata."""
    if not CV_PATH.exists():
        return "[📄 Download CV (PDF)](CV.pdf)"

    size_kb = CV_PATH.stat().st_size / 1024
    mtime = datetime.fromtimestamp(CV_PATH.stat().st_mtime, timezone.utc).strftime("%B %Y")
    sha256 = hashlib.sha256(CV_PATH.read_bytes()).hexdigest()[:8]

    return (
        f'<div align="center">\n'
        f'  <a href="https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_USERNAME}/main/CV.pdf" target="_blank">\n'
        f'    <img src="https://img.shields.io/badge/Download_Resume_PDF-D14836?style=for-the-badge&logo=adobeacrobatreader&logoColor=white" />\n'
        f'  </a>\n'
        f'  <p><sub>📄 <b>File:</b> CV.pdf ({size_kb:.1f} KB) &nbsp;|&nbsp; 🗓️ <b>Updated:</b> {mtime} &nbsp;|&nbsp; 🔒 <b>SHA:</b> <code>{sha256}</code></sub></p>\n'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 6. Dynamic Greeting (IST Timezone)
# ---------------------------------------------------------------------------


def get_dynamic_greeting() -> str:
    """Generate dynamic greeting based on Indian Standard Time (UTC+5:30)."""
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    hour = now_ist.hour

    if 5 <= hour < 12:
        greeting = "Good Morning! 🌅"
    elif 12 <= hour < 17:
        greeting = "Good Afternoon! ☀️"
    elif 17 <= hour < 22:
        greeting = "Good Evening! 🌆"
    else:
        greeting = "Late Night Coding Session! 🦉"

    date_str = now_ist.strftime("%d %B %Y, %I:%M %p IST")
    return f"**{greeting}** &nbsp;•&nbsp; 🕒 *Current Time:* `{date_str}` &nbsp;•&nbsp; 🟢 *Status:* Open for Collaboration & SDE Roles"


# ---------------------------------------------------------------------------
# 7. Helper to Replace Markers in README
# ---------------------------------------------------------------------------


def replace_marker(content: str, marker_name: str, replacement: str) -> str:
    """Replace content between <!-- MARKER:START --> and <!-- MARKER:END -->."""
    start_tag = f"<!-- {marker_name}:START -->"
    end_tag = f"<!-- {marker_name}:END -->"

    if start_tag in content and end_tag in content:
        pattern = re.compile(
            rf"({re.escape(start_tag)})(.*?)({re.escape(end_tag)})",
            re.DOTALL,
        )
        return pattern.sub(rf"\1\n{replacement}\n\3", content)

    return content


def update_profile_readme() -> bool:
    """Update all dynamic sections of README.md."""
    if not README_PATH.exists():
        logger.error("[ERROR] README.md not found at %s", README_PATH)
        return False

    content = README_PATH.read_text(encoding="utf-8")

    # 1. LeetCode Stats
    logger.info("[INFO] Fetching LeetCode stats...")
    leetcode_stats = fetch_leetcode_stats()
    leetcode_md = generate_leetcode_section(leetcode_stats)
    content = replace_marker(content, "LEETCODE", leetcode_md)

    # 2. Recent Activity
    logger.info("[INFO] Fetching GitHub recent activity...")
    activities = fetch_recent_activity()
    activity_md = generate_recent_activity_section(activities)
    content = replace_marker(content, "RECENT_ACTIVITY", activity_md)

    # 3. Top Repositories
    logger.info("[INFO] Fetching top repositories...")
    repos = fetch_top_repositories()
    repos_md = generate_top_repos_section(repos)
    content = replace_marker(content, "TOP_REPOS", repos_md)

    # 4. Daily Quote
    quote_md = get_daily_quote()
    content = replace_marker(content, "DAILY_QUOTE", quote_md)

    # 5. Resume Info
    resume_md = get_resume_info()
    content = replace_marker(content, "RESUME_INFO", resume_md)

    # 6. Dynamic Greeting
    greeting_md = get_dynamic_greeting()
    content = replace_marker(content, "DYNAMIC_GREETING", greeting_md)

    # 7. Community Wall (Stargazers & Followers)
    logger.info("[INFO] Fetching community stargazers & followers...")
    stargazers = fetch_stargazers()
    followers = fetch_followers()
    community_md = generate_community_wall_section(stargazers, followers)
    content = replace_marker(content, "COMMUNITY_WALL", community_md)

    README_PATH.write_text(content, encoding="utf-8")
    logger.info("[INFO] Successfully updated README.md with all dynamic profile automations!")
    return True


if __name__ == "__main__":
    update_profile_readme()
