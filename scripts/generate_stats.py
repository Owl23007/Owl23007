#!/usr/bin/env python3
"""
Generate GitHub stats cards using GitHub API
"""
import os
import requests
from datetime import datetime


def get_github_stats(username, token):
    """Fetch GitHub user statistics"""
    headers = {'Authorization': f'token {token}'} if token else {}
    
    try:
        # Get user info
        user_response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers,
            timeout=10
        )
        
        if user_response.status_code != 200:
            print(f"Warning: Failed to fetch user data (status {user_response.status_code})")
            return get_fallback_stats(username)
        
        user_data = user_response.json()
        
        # Get user's repositories
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100',
            headers=headers,
            timeout=10
        )
        
        if repos_response.status_code == 200:
            repos = repos_response.json()
        else:
            repos = []
        
        # Calculate stats
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        total_repos = user_data.get('public_repos', 0)
        
        # Get total commits (approximate from events)
        try:
            events_response = requests.get(
                f'https://api.github.com/users/{username}/events/public?per_page=100',
                headers=headers,
                timeout=10
            )
            events = events_response.json() if events_response.status_code == 200 else []
            commit_events = [e for e in events if e.get('type') == 'PushEvent']
            recent_commits = sum(len(e.get('payload', {}).get('commits', [])) for e in commit_events)
        except (requests.RequestException, requests.JSONDecodeError, KeyError):
            recent_commits = 0
        
        return {
            'name': user_data.get('name', username),
            'total_repos': total_repos,
            'total_stars': total_stars,
            'total_forks': total_forks,
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'recent_commits': recent_commits
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return get_fallback_stats(username)


def get_fallback_stats(username):
    """Return fallback stats when API is unavailable"""
    return {
        'name': username,
        'total_repos': 0,
        'total_stars': 0,
        'total_forks': 0,
        'followers': 0,
        'following': 0,
        'recent_commits': 0
    }


def get_top_languages(username, token):
    """Get top programming languages used"""
    headers = {'Authorization': f'token {token}'} if token else {}
    
    try:
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100',
            headers=headers,
            timeout=10
        )
        
        if repos_response.status_code != 200:
            return []
        
        repos = repos_response.json()
        
        language_stats = {}
        for repo in repos:
            if repo.get('fork'):
                continue
            
            # Get languages for this repo
            lang_url = repo.get('languages_url')
            if lang_url:
                try:
                    lang_response = requests.get(lang_url, headers=headers, timeout=5)
                    if lang_response.status_code == 200:
                        languages = lang_response.json()
                        for lang, bytes_count in languages.items():
                            if lang:
                                language_stats[lang] = language_stats.get(lang, 0) + bytes_count
                except (requests.RequestException, requests.JSONDecodeError, KeyError):
                    continue
        
        # Sort by usage
        sorted_langs = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)
        return sorted_langs[:6]  # Top 6 languages
    except Exception as e:
        print(f"Error fetching languages: {e}")
        return []


def get_repo_info(username, repo_name, token):
    """Get repository information"""
    headers = {'Authorization': f'token {token}'} if token else {}
    
    try:
        response = requests.get(
            f'https://api.github.com/repos/{username}/{repo_name}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'name': data.get('name', repo_name),
                'description': data.get('description', 'No description provided'),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'language': data.get('language') or 'Unknown'
            }
    except Exception as e:
        print(f"Error fetching repo {repo_name}: {e}")
    
    # Return fallback
    return {
        'name': repo_name,
        'description': 'Repository information',
        'stars': 0,
        'forks': 0,
        'language': 'Unknown'
    }


def generate_stats_card(stats):
    """Generate SVG for GitHub stats"""
    svg = f'''<svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f2027"/>
      <stop offset="50%" style="stop-color:#203a43"/>
      <stop offset="100%" style="stop-color:#2c5364"/>
    </linearGradient>
    <style>
      .header {{ fill: #70e1f5; font-size: 18px; font-weight: 600; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .stat-label {{ fill: #a8dadc; font-size: 14px; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .stat-value {{ fill: #ffffff; font-size: 14px; font-weight: 700; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .icon {{ fill: #70e1f5; }}
    </style>
  </defs>
  
  <rect width="495" height="195" fill="url(#bg)" stroke="#3d5a80" stroke-width="1" rx="8"/>
  
  <text x="25" y="35" class="header">✨ {stats['name']}'s GitHub Stats</text>
  <line x1="25" y1="45" x2="470" y2="45" stroke="#3d5a80" stroke-width="0.5"/>
  
  <g transform="translate(25, 72)">
    <text y="0" class="stat-label">📁 Total Repos</text>
    <text x="200" y="0" class="stat-value">{stats['total_repos']}</text>
  </g>
  
  <g transform="translate(25, 97)">
    <text y="0" class="stat-label">⭐ Total Stars</text>
    <text x="200" y="0" class="stat-value">{stats['total_stars']}</text>
  </g>
  
  <g transform="translate(25, 122)">
    <text y="0" class="stat-label">🔱 Total Forks</text>
    <text x="200" y="0" class="stat-value">{stats['total_forks']}</text>
  </g>
  
  <g transform="translate(25, 147)">
    <text y="0" class="stat-label">👥 Followers</text>
    <text x="200" y="0" class="stat-value">{stats['followers']}</text>
  </g>
  
  <g transform="translate(270, 72)">
    <text y="0" class="stat-label">➡️ Following</text>
    <text x="150" y="0" class="stat-value">{stats['following']}</text>
  </g>
  
  <text x="470" y="185" style="fill: #5c8a97; font-size: 10px; font-family: 'Segoe UI', Ubuntu, sans-serif;" text-anchor="end">Updated {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>'''
    return svg


def generate_languages_card(languages):
    """Generate SVG for top languages"""
    if not languages:
        return '<svg width="240" height="195" xmlns="http://www.w3.org/2000/svg"><rect width="240" height="195" fill="#0d1117"/></svg>'
    
    total_bytes = sum(bytes_count for _, bytes_count in languages)
    
    # Language colors (simplified)
    lang_colors = {
        'Python': '#3572A5',
        'JavaScript': '#f1e05a',
        'TypeScript': '#2b7489',
        'Java': '#b07219',
        'C++': '#f34b7d',
        'C': '#555555',
        'Go': '#00ADD8',
        'Rust': '#dea584',
        'Ruby': '#701516',
        'PHP': '#4F5D95',
        'Vue': '#41b883',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Shell': '#89e051',
        'Kotlin': '#A97BFF',
    }
    
    svg_parts = ['''<svg width="240" height="195" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="50%" style="stop-color:#16213e"/>
      <stop offset="100%" style="stop-color:#0f3460"/>
    </linearGradient>
    <style>
      .lang-name { fill: #e0e0e0; font-size: 12px; font-family: 'Segoe UI', Ubuntu, sans-serif; }
      .lang-percent { fill: #a8dadc; font-size: 11px; font-family: 'Segoe UI', Ubuntu, sans-serif; }
    </style>
  </defs>
  
  <rect width="240" height="195" fill="url(#bg)" stroke="#3d5a80" stroke-width="1" rx="8"/>
  
  <text x="120" y="30" style="fill: #70e1f5; font-size: 16px; font-weight: 600; font-family: 'Segoe UI', Ubuntu, sans-serif;" text-anchor="middle">🏆 Top Languages</text>
  <line x1="20" y1="40" x2="220" y2="40" stroke="#3d5a80" stroke-width="0.5"/>
''']
    
    y_offset = 60
    for i, (lang, bytes_count) in enumerate(languages):
        percentage = (bytes_count / total_bytes) * 100
        color = lang_colors.get(lang, '#858585')
        
        svg_parts.append(f'''
  <g transform="translate(20, {y_offset + i * 22})">
    <circle cx="5" cy="-3" r="5" fill="{color}"/>
    <text x="15" y="0" class="lang-name">{lang}</text>
    <text x="200" y="0" class="lang-percent" text-anchor="end">{percentage:.1f}%</text>
  </g>''')
    
    svg_parts.append(f'''
  <text x="220" y="185" style="fill: #5c8a97; font-size: 10px; font-family: 'Segoe UI', Ubuntu, sans-serif;" text-anchor="end">Updated {datetime.now().strftime('%Y-%m-%d')}</text>
</svg>''')
    
    return ''.join(svg_parts)


def generate_repo_pin_card(repo_info):
    """Generate SVG for repository pin card"""
    if not repo_info:
        repo_info = {
            'name': 'Repository',
            'description': 'No description',
            'stars': 0,
            'forks': 0,
            'language': 'Unknown'
        }
    
    # Truncate description if too long
    desc = repo_info['description'] or 'No description provided'
    if len(desc) > 60:
        desc = desc[:57] + '...'
    
    # Language-specific colors
    lang_colors = {
        'Python': '#3572A5', 'JavaScript': '#f1e05a', 'TypeScript': '#2b7489',
        'Java': '#b07219', 'C++': '#f34b7d', 'C': '#555555', 'Go': '#00ADD8',
        'Rust': '#dea584', 'Vue': '#41b883', 'HTML': '#e34c26', 'CSS': '#563d7c',
        'Kotlin': '#A97BFF', 'Shell': '#89e051',
    }
    lang_color = lang_colors.get(repo_info['language'], '#858585')
    
    svg = f'''<svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e1e2e"/>
      <stop offset="100%" style="stop-color:#302d41"/>
    </linearGradient>
    <style>
      .repo-name {{ fill: #89b4fa; font-size: 16px; font-weight: 600; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .repo-desc {{ fill: #a6adc8; font-size: 12px; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .repo-stat {{ fill: #cdd6f4; font-size: 12px; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
      .repo-lang {{ fill: #cdd6f4; font-size: 12px; font-family: 'Segoe UI', Ubuntu, sans-serif; }}
    </style>
  </defs>
  
  <rect width="400" height="120" fill="url(#bg)" stroke="#45475a" stroke-width="1" rx="8"/>
  
  <text x="15" y="30" class="repo-name">📦 {repo_info['name']}</text>
  <text x="15" y="55" class="repo-desc">{desc}</text>
  
  <g transform="translate(15, 95)">
    <circle cx="5" cy="-3" r="5" fill="{lang_color}"/>
    <text x="15" y="0" class="repo-lang">{repo_info['language']}</text>
  </g>
  
  <g transform="translate(150, 95)">
    <text y="0" class="repo-stat">⭐ {repo_info['stars']}</text>
  </g>
  
  <g transform="translate(230, 95)">
    <text y="0" class="repo-stat">🔱 {repo_info['forks']}</text>
  </g>
</svg>'''
    return svg


def main():
    username = os.environ.get('GITHUB_REPOSITORY_OWNER', 'Owl23007')
    token = os.environ.get('GITHUB_TOKEN', '')
    
    print(f"Generating stats for user: {username}")
    
    try:
        # Generate stats card
        print("Fetching GitHub stats...")
        stats = get_github_stats(username, token)
        stats_svg = generate_stats_card(stats)
        with open('assets/stats.svg', 'w', encoding='utf-8') as f:
            f.write(stats_svg)
        print("✓ Generated stats.svg")
        
        # Generate languages card
        print("Fetching top languages...")
        languages = get_top_languages(username, token)
        langs_svg = generate_languages_card(languages)
        with open('assets/top-langs.svg', 'w', encoding='utf-8') as f:
            f.write(langs_svg)
        print("✓ Generated top-langs.svg")
        
        # Generate repo pin cards
        repos_to_pin = [
            ('simple-my-blog', 'simple-my-blog-pin.svg'),
            ('Linx', 'linx-pin.svg')
        ]
        
        for repo_name, filename in repos_to_pin:
            print(f"Fetching {repo_name} info...")
            repo_info = get_repo_info(username, repo_name, token)
            repo_svg = generate_repo_pin_card(repo_info)
            with open(f'assets/{filename}', 'w', encoding='utf-8') as f:
                f.write(repo_svg)
            print(f"✓ Generated {filename}")
        
        print("\n✨ All stats generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating stats: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
