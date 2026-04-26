#!/usr/bin/env python3
"""Generate light-theme SVG assets for the profile README."""
from __future__ import annotations

import html
import os
import textwrap
from datetime import datetime
from pathlib import Path

import requests


ASSETS_DIR = Path("assets")
FONT_STACK = "'Segoe UI', Ubuntu, Arial, sans-serif"

LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Vue": "#41b883",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "Kotlin": "#A97BFF",
}

FEATURED_REPO_FALLBACKS = {
    "simple-my-blog": {
        "description": "A personal introduction website quickly built with VitePress.",
        "language": "TypeScript",
    },
    "Linx": {
        "description": "A lightweight toolkit for building and exploring useful desktop workflows.",
        "language": "TypeScript",
    },
    "nova-http": {
        "description": "A lightweight, high-performance Node.js web framework built on modern TypeScript.",
        "language": "TypeScript",
    },
    "synapse-android": {
        "description": "A lightweight Android calendar app with built-in AI capabilities.",
        "language": "Kotlin",
    },
}


def escape(value) -> str:
    """Escape dynamic text before embedding it in SVG."""
    return html.escape(str(value), quote=True)


def github_headers(token: str) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Owl23007-profile-generator",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_github_stats(username: str, token: str) -> dict[str, int | str]:
    """Fetch GitHub user statistics."""
    headers = github_headers(token)

    try:
        user_response = requests.get(
            f"https://api.github.com/users/{username}",
            headers=headers,
            timeout=10,
        )

        if user_response.status_code != 200:
            print(f"Warning: failed to fetch user data ({user_response.status_code})")
            return get_fallback_stats(username)

        user_data = user_response.json()

        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100",
            headers=headers,
            timeout=10,
        )
        repos = repos_response.json() if repos_response.status_code == 200 else []

        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)

        try:
            events_response = requests.get(
                f"https://api.github.com/users/{username}/events/public?per_page=100",
                headers=headers,
                timeout=10,
            )
            events = events_response.json() if events_response.status_code == 200 else []
            push_events = [event for event in events if event.get("type") == "PushEvent"]
            recent_commits = sum(
                len(event.get("payload", {}).get("commits", [])) for event in push_events
            )
        except (requests.RequestException, requests.JSONDecodeError, KeyError):
            recent_commits = 0

        return {
            "name": user_data.get("name") or username,
            "total_repos": user_data.get("public_repos", 0),
            "total_stars": total_stars,
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "recent_commits": recent_commits,
        }
    except Exception as exc:
        print(f"Error fetching stats: {exc}")
        return get_fallback_stats(username)


def get_fallback_stats(username: str) -> dict[str, int | str]:
    """Return fallback stats when the API is unavailable."""
    return {
        "name": username,
        "total_repos": 0,
        "total_stars": 0,
        "followers": 0,
        "following": 0,
        "recent_commits": 0,
    }


def get_top_languages(username: str, token: str) -> list[tuple[str, int]]:
    """Get top programming languages used across non-fork repositories."""
    headers = github_headers(token)

    try:
        repos_response = requests.get(
            f"https://api.github.com/users/{username}/repos?per_page=100",
            headers=headers,
            timeout=10,
        )

        if repos_response.status_code != 200:
            return []

        language_stats: dict[str, int] = {}
        for repo in repos_response.json():
            if repo.get("fork"):
                continue

            lang_url = repo.get("languages_url")
            if not lang_url:
                continue

            try:
                lang_response = requests.get(lang_url, headers=headers, timeout=5)
                if lang_response.status_code == 200:
                    for lang, bytes_count in lang_response.json().items():
                        language_stats[lang] = language_stats.get(lang, 0) + bytes_count
            except (requests.RequestException, requests.JSONDecodeError, KeyError):
                continue

        return sorted(language_stats.items(), key=lambda item: item[1], reverse=True)[:6]
    except Exception as exc:
        print(f"Error fetching languages: {exc}")
        return []


def get_repo_info(username: str, repo_name: str, token: str) -> dict[str, int | str]:
    """Get repository information."""
    fallback = FEATURED_REPO_FALLBACKS.get(repo_name, {})
    commits = get_repo_commit_count(username, repo_name, token)
    try:
        response = requests.get(
            f"https://api.github.com/repos/{username}/{repo_name}",
            headers=github_headers(token),
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name", repo_name),
                "description": fallback.get("description")
                or data.get("description")
                or "No description provided",
                "stars": data.get("stargazers_count", 0),
                "commits": commits,
                "language": fallback.get("language") or data.get("language") or "Unknown",
            }
    except Exception as exc:
        print(f"Error fetching repo {repo_name}: {exc}")

    return {
        "name": repo_name,
        "description": fallback.get("description", "Repository information"),
        "stars": 0,
        "commits": commits,
        "language": fallback.get("language", "Unknown"),
    }


def get_repo_commit_count(username: str, repo_name: str, token: str) -> int:
    """Estimate repository commit count from GitHub pagination metadata."""
    try:
        response = requests.get(
            f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=1",
            headers=github_headers(token),
            timeout=10,
        )

        if response.status_code != 200:
            return 0

        link_header = response.headers.get("Link", "")
        for part in link_header.split(","):
            if 'rel="last"' not in part:
                continue
            marker = "page="
            if marker in part:
                page_value = part.split(marker, 1)[1].split(">", 1)[0].split("&", 1)[0]
                return int(page_value)

        return len(response.json())
    except Exception as exc:
        print(f"Error fetching commit count for {repo_name}: {exc}")
        return 0


def generate_header_card() -> str:
    """Generate the profile header SVG."""
    return f'''<svg width="800" height="220" viewBox="0 0 800 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Owl23007 profile header">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="58%" stop-color="#f8fcff"/>
      <stop offset="100%" stop-color="#eef7ff"/>
    </linearGradient>
    <linearGradient id="panel" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f3f9ff"/>
    </linearGradient>
    <style>
      .eyebrow {{ fill: #2f80ed; font-size: 13px; font-weight: 700; font-family: {FONT_STACK}; }}
      .title {{ fill: #102033; font-size: 38px; font-weight: 780; font-family: {FONT_STACK}; }}
      .subtitle {{ fill: #36536f; font-size: 16px; font-family: {FONT_STACK}; }}
      .tag {{ fill: #36536f; font-size: 12px; font-weight: 650; font-family: {FONT_STACK}; }}
      .code {{ fill: #5f7185; font-size: 12px; font-family: Consolas, 'Cascadia Code', monospace; }}
      .kw {{ fill: #2f80ed; font-weight: 700; }}
      .fn {{ fill: #27ae60; font-weight: 700; }}
      .str {{ fill: #d9822b; }}
      .punct {{ fill: #7b8da0; }}
    </style>
  </defs>

  <rect x="1" y="1" width="798" height="218" rx="16" fill="url(#bg)" stroke="#dbe8f6" stroke-width="2"/>
  <circle cx="676" cy="42" r="58" fill="#dff1ff" opacity="0.95"/>
  <circle cx="764" cy="142" r="36" fill="#fff0d9" opacity="0.95"/>
  <circle cx="746" cy="190" r="24" fill="#e5f8ec" opacity="0.9"/>

  <rect x="46" y="38" width="106" height="32" rx="16" fill="#e8f2ff"/>
  <text x="99" y="59" class="eyebrow" text-anchor="middle">Owl23007</text>

  <text x="46" y="116" class="title">Hi, I'm Owl23007</text>
  <text x="46" y="148" class="subtitle">Building tools, interfaces, and small experiments from Wuhan.</text>

  <g transform="translate(46, 174)">
    <rect width="68" height="26" rx="13" fill="#eef6ff" stroke="#dbe8f6"/>
    <text x="34" y="17" class="tag" text-anchor="middle">Python</text>
    <rect x="78" width="52" height="26" rx="13" fill="#fff7ec" stroke="#f4dfc2"/>
    <text x="104" y="17" class="tag" text-anchor="middle">Java</text>
    <rect x="140" width="50" height="26" rx="13" fill="#ecfbf3" stroke="#cfeedd"/>
    <text x="165" y="17" class="tag" text-anchor="middle">Vue</text>
    <rect x="200" width="72" height="26" rx="13" fill="#f3f8ff" stroke="#dbe8f6"/>
    <text x="236" y="17" class="tag" text-anchor="middle">Android</text>
    <rect x="282" width="58" height="26" rx="13" fill="#f7f8fb" stroke="#dfe6ef"/>
    <text x="311" y="17" class="tag" text-anchor="middle">Unity</text>
  </g>

  <g transform="translate(512, 38)">
    <rect width="236" height="146" rx="14" fill="url(#panel)" fill-opacity="0.94" stroke="#d5e5f5" stroke-width="2"/>
    <circle cx="24" cy="24" r="5" fill="#f2994a"/>
    <circle cx="42" cy="24" r="5" fill="#27ae60"/>
    <circle cx="60" cy="24" r="5" fill="#2f80ed"/>
    <text x="24" y="50" class="code"><tspan class="kw">new</tspan> <tspan class="fn">Promise</tspan><tspan class="punct">(</tspan>resolve <tspan class="punct">=&gt; {{</tspan></text>
    <text x="24" y="72" class="code">  console<tspan class="punct">.</tspan><tspan class="fn">log</tspan><tspan class="punct">(</tspan><tspan class="str">'coding, searching,</tspan></text>
    <text x="24" y="94" class="code"><tspan class="str">  and distracted...'</tspan><tspan class="punct">);</tspan></text>
    <text x="24" y="116" class="code">  <tspan class="fn">resolve</tspan><tspan class="punct">(</tspan><tspan class="str">'DONE!'</tspan><tspan class="punct">);</tspan></text>
    <text x="24" y="138" class="code"><tspan class="punct">}}</tspan><tspan class="punct">).</tspan><tspan class="fn">then</tspan><tspan class="punct">(</tspan>console<tspan class="punct">.</tspan>log<tspan class="punct">)</tspan></text>
  </g>

  <path d="M494 150 C502 138, 506 126, 510 116" fill="none" stroke="#2f80ed" stroke-width="3" stroke-linecap="round" opacity="0.65"/>
  <circle cx="494" cy="150" r="6" fill="#2f80ed"/>
  <circle cx="510" cy="116" r="5" fill="#2f80ed"/>
</svg>'''


def generate_tech_stack_card() -> str:
    """Generate SVG for the technology stack section."""
    groups = [
        (
            "Core Development",
            "#2f80ed",
            [
                ("Python", "#3572A5"),
                ("Java", "#b07219"),
                ("Vue", "#41b883"),
                ("TypeScript", "#3178c6"),
            ],
        ),
        (
            "Apps & Tooling",
            "#27ae60",
            [
                ("Android", "#3DDC84"),
                ("Electron", "#47848F"),
                ("VitePress", "#646CFF"),
                ("GitHub Actions", "#2088FF"),
            ],
        ),
        (
            "Creative Lab",
            "#f2994a",
            [
                ("Unity", "#222222"),
                ("Blender", "#F5792A"),
                ("FL Studio", "#FB5607"),
                ("3D / Music", "#8E7CC3"),
            ],
        ),
    ]

    cards: list[str] = []
    for index, (title, accent, items) in enumerate(groups):
        x = 32 + index * 250
        rows = []
        for row_index, (name, color) in enumerate(items):
            y = 68 + row_index * 24
            rows.append(f'''
      <g transform="translate(0, {y})">
        <circle cx="8" cy="-4" r="5" fill="{color}"/>
        <text x="22" y="0" class="item">{escape(name)}</text>
      </g>''')

        cards.append(f'''
  <g transform="translate({x}, 38)">
    <rect width="226" height="152" rx="14" fill="#ffffff" stroke="#dbe8f6" stroke-width="2"/>
    <rect x="14" y="14" width="198" height="30" rx="15" fill="#f3f8ff"/>
    <circle cx="31" cy="29" r="5" fill="{accent}"/>
    <text x="46" y="34" class="group-title">{escape(title)}</text>
    <g transform="translate(22, 0)">
      {''.join(rows)}
    </g>
  </g>''')

    return f'''<svg width="800" height="218" viewBox="0 0 800 218" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Technology stack">
  <defs>
    <linearGradient id="stack-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="58%" stop-color="#f8fcff"/>
      <stop offset="100%" stop-color="#eef7ff"/>
    </linearGradient>
    <style>
      .title {{ fill: #102033; font-size: 18px; font-weight: 760; font-family: {FONT_STACK}; }}
      .subtitle {{ fill: #5f7185; font-size: 12px; font-family: {FONT_STACK}; }}
      .group-title {{ fill: #102033; font-size: 13px; font-weight: 720; font-family: {FONT_STACK}; }}
      .item {{ fill: #36536f; font-size: 12px; font-weight: 620; font-family: {FONT_STACK}; }}
    </style>
  </defs>

  <rect x="1" y="1" width="798" height="216" rx="16" fill="url(#stack-bg)" stroke="#dbe8f6" stroke-width="2"/>
  <text x="32" y="26" class="title">Tech Stack</text>
  <text x="140" y="26" class="subtitle">Languages, platforms, and creative tools I use often.</text>
  {''.join(cards)}
</svg>'''


def generate_stats_card(stats: dict[str, int | str]) -> str:
    """Generate SVG for GitHub stats."""
    today = datetime.now().strftime("%Y-%m-%d")
    return f'''<svg width="495" height="195" viewBox="0 0 495 195" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats">
  <defs>
    <style>
      .header {{ fill: #102033; font-size: 18px; font-weight: 700; font-family: {FONT_STACK}; }}
      .label {{ fill: #5f7185; font-size: 13px; font-family: {FONT_STACK}; }}
      .value {{ fill: #102033; font-size: 18px; font-weight: 760; font-family: {FONT_STACK}; }}
      .foot {{ fill: #7b8da0; font-size: 10px; font-family: {FONT_STACK}; }}
    </style>
  </defs>

  <rect x="1" y="1" width="493" height="193" rx="10" fill="#ffffff" stroke="#dbe8f6" stroke-width="2"/>
  <rect x="18" y="17" width="459" height="42" rx="8" fill="#f3f8ff"/>
  <text x="247.5" y="44" class="header" text-anchor="middle">GitHub Stats</text>

  <g transform="translate(30, 88)">
    <text class="label">Repositories</text>
    <text y="24" class="value">{stats["total_repos"]}</text>
  </g>
  <g transform="translate(180, 88)">
    <text class="label">Stars</text>
    <text y="24" class="value">{stats["total_stars"]}</text>
  </g>
  <g transform="translate(315, 88)">
    <text class="label">Recent Commits</text>
    <text y="24" class="value">{stats["recent_commits"]}</text>
  </g>

  <g transform="translate(30, 146)">
    <text class="label">Followers</text>
    <text x="92" class="value">{stats["followers"]}</text>
  </g>
  <g transform="translate(220, 146)">
    <text class="label">Following</text>
    <text x="92" class="value">{stats["following"]}</text>
  </g>

  <text x="472" y="178" class="foot" text-anchor="end">Updated {today}</text>
</svg>'''


def generate_languages_card(languages: list[tuple[str, int]]) -> str:
    """Generate SVG for top languages."""
    today = datetime.now().strftime("%Y-%m-%d")
    if not languages:
        languages = [("Python", 1), ("Java", 1), ("Vue", 1)]

    total_bytes = sum(bytes_count for _, bytes_count in languages) or 1
    rows: list[str] = []
    for index, (lang, bytes_count) in enumerate(languages):
        percentage = (bytes_count / total_bytes) * 100
        bar_width = max(4, min(152, percentage * 1.52))
        color = LANG_COLORS.get(lang, "#858585")
        y = 58 + index * 21
        rows.append(f'''
  <g transform="translate(20, {y})">
    <circle cx="5" cy="-4" r="5" fill="{color}"/>
    <text x="17" y="0" class="name">{escape(lang)}</text>
    <text x="200" y="0" class="percent" text-anchor="end">{percentage:.1f}%</text>
    <rect x="17" y="6" width="152" height="5" rx="2.5" fill="#edf4fb"/>
    <rect x="17" y="6" width="{bar_width:.1f}" height="5" rx="2.5" fill="{color}"/>
  </g>''')

    return f'''<svg width="240" height="195" viewBox="0 0 240 195" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Top languages">
  <defs>
    <style>
      .title {{ fill: #102033; font-size: 16px; font-weight: 700; font-family: {FONT_STACK}; }}
      .name {{ fill: #36536f; font-size: 12px; font-family: {FONT_STACK}; }}
      .percent {{ fill: #5f7185; font-size: 11px; font-family: {FONT_STACK}; }}
      .foot {{ fill: #7b8da0; font-size: 10px; font-family: {FONT_STACK}; }}
    </style>
  </defs>

  <rect x="1" y="1" width="238" height="193" rx="10" fill="#ffffff" stroke="#dbe8f6" stroke-width="2"/>
  <rect x="15" y="16" width="210" height="30" rx="8" fill="#f3f8ff"/>
  <text x="120" y="36" class="title" text-anchor="middle">Top Languages</text>
  {''.join(rows)}
  <text x="220" y="178" class="foot" text-anchor="end">Updated {today}</text>
</svg>'''


def generate_repo_pin_card(repo_info: dict[str, int | str]) -> str:
    """Generate SVG for repository pin card."""
    description = str(repo_info.get("description") or "No description provided")
    desc_lines = textwrap.wrap(
        description,
        width=52,
        max_lines=2,
        placeholder="...",
        break_long_words=False,
        break_on_hyphens=False,
    ) or ["No description provided"]
    if len(desc_lines) == 1:
        desc_lines.append("")

    language = str(repo_info.get("language") or "Unknown")
    lang_color = LANG_COLORS.get(language, "#858585")

    return f'''<svg width="400" height="120" viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(repo_info.get("name", "Repository"))} repository card">
  <defs>
    <style>
      .repo-name {{ fill: #102033; font-size: 16px; font-weight: 700; font-family: {FONT_STACK}; }}
      .repo-desc {{ fill: #5f7185; font-size: 12px; font-family: {FONT_STACK}; }}
      .repo-stat {{ fill: #36536f; font-size: 12px; font-family: {FONT_STACK}; }}
      .star-icon {{ fill: #f2994a; }}
      .commit-icon {{ fill: none; stroke: #2f80ed; stroke-width: 1.8; stroke-linecap: round; }}
    </style>
  </defs>

  <rect x="1" y="1" width="398" height="118" rx="10" fill="#ffffff" stroke="#dbe8f6" stroke-width="2"/>
  <rect x="14" y="14" width="372" height="34" rx="8" fill="#f8fbff"/>
  <text x="26" y="36" class="repo-name">{escape(repo_info.get("name", "Repository"))}</text>
  <text x="26" y="62" class="repo-desc">{escape(desc_lines[0])}</text>
  <text x="26" y="78" class="repo-desc">{escape(desc_lines[1])}</text>

  <g transform="translate(26, 102)">
    <circle cx="5" cy="-4" r="5" fill="{lang_color}"/>
    <text x="17" y="0" class="repo-stat">{escape(language)}</text>
  </g>
  <g transform="translate(170, 102)">
    <path class="star-icon" d="M6 -13 L7.9 -8.5 L12.8 -8.1 L9.1 -5 L10.2 -0.2 L6 -2.7 L1.8 -0.2 L2.9 -5 L-0.8 -8.1 L4.1 -8.5 Z"/>
    <text x="19" y="0" class="repo-stat">{repo_info.get("stars", 0)}</text>
  </g>
  <g transform="translate(244, 102)">
    <path class="commit-icon" d="M0 -6 H4 M14 -6 H18"/>
    <circle class="commit-icon" cx="9" cy="-6" r="4"/>
    <text x="26" y="0" class="repo-stat">{repo_info.get("commits", 0)}</text>
  </g>
</svg>'''


def write_asset(filename: str, content: str) -> None:
    ASSETS_DIR.mkdir(exist_ok=True)
    (ASSETS_DIR / filename).write_text(content, encoding="utf-8")
    print(f"Generated {filename}")


def main() -> None:
    username = os.environ.get("GITHUB_REPOSITORY_OWNER", "Owl23007")
    token = os.environ.get("GITHUB_TOKEN", "")

    print(f"Generating light-theme profile assets for user: {username}")

    write_asset("header.svg", generate_header_card())
    write_asset("tech-stack.svg", generate_tech_stack_card())

    print("Fetching GitHub stats...")
    stats = get_github_stats(username, token)
    write_asset("stats.svg", generate_stats_card(stats))

    print("Fetching top languages...")
    languages = get_top_languages(username, token)
    write_asset("top-langs.svg", generate_languages_card(languages))

    repos_to_pin = [
        ("simple-my-blog", "simple-my-blog-pin.svg"),
        ("Linx", "linx-pin.svg"),
        ("nova-http", "nova-http-pin.svg"),
        ("synapse-android", "synapse-android-pin.svg"),
    ]

    for repo_name, filename in repos_to_pin:
        print(f"Fetching {repo_name} info...")
        repo_info = get_repo_info(username, repo_name, token)
        write_asset(filename, generate_repo_pin_card(repo_info))

    print("All assets generated successfully.")


if __name__ == "__main__":
    main()
