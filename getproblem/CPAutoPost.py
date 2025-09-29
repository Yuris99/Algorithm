import sys
import re  # 정규표현식 라이브러리 추가
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from datetime import datetime
from abc import ABC, abstractmethod

# ==================================================================
# 사용자 설정 (USER CONFIG)
# ==================================================================
# 각 플랫폼에 맞는 본인의 핸들을 정확하게 입력해주세요.
HANDLES = {
    "codeforces": "Yuris",  # <-- 🚨 본인의 Codeforces 핸들로 변경!
    "atcoder": "Yuris"      # <-- 🚨 본인의 AtCoder 핸들로 변경!
}
# ==================================================================


# 마크다운 템플릿 (사용자 예시 기반으로 수정)
MARKDOWN_TEMPLATE = """
---
title: {{ contest.title }}
categories: {{ contest.type }}
tags: {{ contest.type | lower }} {{ contest.tag_suffix }}
article_header:
  type: cover
---
## Contest info

[> Go to {{ contest.type }} Contests list](../{{ contest.type | lower }})

| Title | <a href="{{ contest.link }}">{{ contest.title_short }}</a> |
{% if contest.division %}| Division | {{ contest.division }} |
{% endif %}| Date | {{ contest.date }} |
| Official | {{ "Rated" if player.is_rated else "Unrated" }} |
| Rank | {{ player.rank }} |
| Performance | <strong><span style="color:{{ player.performance_color }}">{{ player.performance }}</span></strong> |
| Rating | <strong><span style="color:{{ player.rating_color }}">{{ player.new_rating }}</span></strong>  <span style="color:{{ player.rating_change_color }}">({{ player.rating_change_str }})</span> |

## Problems

| <strong>#</strong> | <strong>Name</strong> | <strong> Solved </strong> |
| :---: | --- | :---: |
{% for problem in problems %}
| {{ problem.index }} | {{ problem.name }} | {{ problem.status_html }} |
{%- endfor %}

## Solution
{% for problem in problems %}
### {{ problem.index }}. {{ problem.name }}
#### 요약

##### 제한

#### 풀이

{% endfor %}
"""

# --- 유틸리티 함수 ---
def get_color_by_value(value, platform):
    if value is None or not isinstance(value, int): return "#000000"
    color_map = {
        "codeforces": [(1200, "#808080"), (1400, "#478000"), (1600, "#77DDBB"), 
                       (1900, "#0000FF"), (2100, "#AA00AA"), (2400, "#FF8C00")],
        "atcoder": [(400, "#808080"), (800, "#804000"), (1200, "#008000"), 
                    (1600, "#00C0C0"), (2000, "#0000FF"), (2400, "#C0C000"), 
                    (2800, "#FF8000")]
    }
    thresholds = color_map.get(platform, [])
    for limit, color in thresholds:
        if value < limit: return color
    return "#FF0000"

# --- Provider 추상 클래스 ---
class ContestProvider(ABC):
    def __init__(self, platform_name, handle):
        self.platform = platform_name
        self.handle = handle
    @abstractmethod
    def fetch_data(self, contest_id): pass
    def get_filename(self, contest_id):
        return f"{contest_id.replace('_', '-')}_{self.handle}.md"

# --- Codeforces Provider 구현 ---
class CodeforcesProvider(ContestProvider):
    def _call_api(self, method, params):
        url = f"https://codeforces.com/api/{method}"
        try:
            res = requests.get(url, params=params); res.raise_for_status()
            data = res.json()
            if data['status'] == 'OK': return data['result']
        except requests.RequestException: return None
        return None

    def fetch_data(self, contest_id):
        standings = self._call_api('contest.standings', {'contestId': contest_id, 'handles': self.handle, 'showUnofficial': 'true'})
        ratings = self._call_api('contest.ratingChanges', {'contestId': contest_id})
        submissions = self._call_api('user.status', {'handle': self.handle})
        if not standings: return None

        contest_info = standings['contest']
        user_row = standings['rows'][0] if standings['rows'] else None
        user_rating = next((r for r in ratings if r['handle'] == self.handle), None) if ratings else None
        
        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        # Division 파싱 로직 수정 (정규표현식 사용)
        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
        contest_name = contest_info['name']
        div_str = None
        title_short = contest_name
        
        match = re.search(r'\((Div\.\s*\d+)\)', contest_name)
        if match:
            full_div_string_with_parens = match.group(0)  # e.g., "(Div. 4)"
            div_str = match.group(1)  # e.g., "Div. 4"
            title_short = contest_name.replace(full_div_string_with_parens, "").strip()
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        # 수정 끝
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲
        
        contest_data = {
            'type': 'Codeforces', 'tag_suffix': 'cf_summary',
            'title': contest_name,
            'title_short': title_short,
            'division': div_str,
            'date': datetime.fromtimestamp(contest_info['startTimeSeconds']).strftime('%Y / %m / %d'),
            'link': f"https://codeforces.com/contest/{contest_id}",
        }
        
        player_data = {'performance': '1652', 'performance_color': get_color_by_value(1652, 'codeforces')}
        if user_rating:
            change = user_rating['newRating'] - user_rating['oldRating']
            player_data.update({
                'rank': user_rating['rank'], 'is_rated': True,
                'new_rating': user_rating['newRating'],
                'rating_change_str': f"+{change}" if change >= 0 else str(change),
                'rating_change_color': "green" if change >= 0 else "red",
                'rating_color': get_color_by_value(user_rating['newRating'], self.platform),
            })
        else:
            player_data.update({ 'rank': user_row['rank'] if user_row else 'N/A', 'is_rated': user_row['participantType'] != 'UNOFFICIAL' if user_row else False, 'new_rating': 'N/A', 'rating_change_str': 'N/A', 'rating_change_color': '#777777', 'rating_color': '#000000' })
        
        problems_data = []
        end_time = contest_info['startTimeSeconds'] + contest_info.get('durationSeconds', 0)
        for i, prob in enumerate(standings['problems']):
            p_data = {'index': prob['index'], 'name': prob['name'], 'status_html': ''}
            if user_row:
                res = user_row['problemResults'][i]
                if res['points'] > 0: p_data['status_html'] = '<span style="color:green"> solved </span>'
                elif res['rejectedAttemptCount'] > 0: p_data['status_html'] = '<span style="color:red"> failed </span>'
                
            if not p_data['status_html'] and submissions:
                if any(s['problem']['contestId'] == int(contest_id) and s['problem']['index'] == prob['index'] and 
                       s['verdict'] == 'OK' and s['creationTimeSeconds'] > end_time for s in submissions):
                    p_data['status_html'] = '<span style="color:orange"> upsolved </span>'
            problems_data.append(p_data)
            
        return {'contest': contest_data, 'player': player_data, 'problems': problems_data}

class AtcoderProvider(ContestProvider):

    def fetch_data(self, contest_id):
        # 1. 웹페이지 요청
        url = f"https://atcoder.jp/contests/{contest_id}/standings?lang=en"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"--> Failed to fetch AtCoder page: {e}")
            return None
        
        # 2. HTML 파싱
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 3. 데이터 추출
        # Contest 데이터
        contest_title_tag = soup.find('a', class_='contest-title')
        if not contest_title_tag:
            print(f"--> Error: Could not find contest title for '{contest_id}'. Check if the ID is correct.")
            return None
        contest_title = contest_title_tag.get_text(strip=True)
        
        start_time_str = soup.find('time', class_='fixtime-full').get_text(strip=True)
        contest_date = datetime.fromisoformat(start_time_str).strftime('%Y / %m / %d')

        div = None
        if 'abc' in contest_id: div = 'Beginner'
        elif 'arc' in contest_id: div = 'Regular'
        elif 'agc' in contest_id: div = 'Grand'

        contest_data = {
            'type': 'Atcoder', 'tag_suffix': 'ac_summary', 'title': contest_title,
            'title_short': contest_title, 'division': div, 'date': contest_date,
            'link': f"https://atcoder.jp/contests/{contest_id}",
        }

        # Player 데이터
        my_row = soup.find('tr', class_='standings-me')
        if my_row:
            cells = my_row.find_all('td')
            rank = cells[0].get_text(strip=True)
            perf = int(cells[2].get_text(strip=True))
            rating_text = cells[3].get_text(strip=True) # "1234 (+56)"
            
            new_rating = int(rating_text.split()[0])
            change_match = re.search(r'([+-]\d+)', rating_text)
            change = int(change_match.group(1)) if change_match else 0

            player_data = {
                'rank': rank, 'is_rated': True, 'performance': perf,
                'performance_color': get_color_by_value(perf, self.platform),
                'new_rating': new_rating,
                'rating_change_str': f"+{change}" if change >= 0 else str(change),
                'rating_change_color': "green" if change >= 0 else "red",
                'rating_color': get_color_by_value(new_rating, self.platform),
            }
        else: # 미참가 또는 순위표에 없는 경우
            player_data = {'rank': 'N/A', 'is_rated': False, 'performance': 'N/A', 'performance_color': '#000000', 'new_rating': 'N/A', 'rating_change_str': 'N/A', 'rating_change_color': '#777777', 'rating_color': '#000000'}

        # Problems 데이터
        problems_data = []
        header_cells = soup.select('thead th.text-center a')
        problem_map = { a['href'].split('/')[-1]: (a.get_text(strip=True), a.parent.find_next_sibling('th').get_text(strip=True)) for a in header_cells }
        
        if my_row:
            problem_cells = my_row.select('td.standings-result')
            for i, cell in enumerate(problem_cells):
                problem_id = list(problem_map.keys())[i]
                index, name = problem_map[problem_id]
                status_html = ''
                if 'ac' in cell.get('class', []):
                    status_html = '<span style="color:green"> solved </span>'
                elif cell.find('span', class_='wa'):
                    status_html = '<span style="color:red"> failed </span>'
                problems_data.append({'index': index, 'name': name, 'status_html': status_html})
        else: # 미참가 시 문제 목록만 생성
            for pid, (index, name) in problem_map.items():
                problems_data.append({'index': index, 'name': name, 'status_html': ''})
                
        return {'contest': contest_data, 'player': player_data, 'problems': problems_data}

# --- 메인 실행 로직 ---
def main():
    if len(sys.argv) != 3:
        print("Usage: python CPAutoPost.py <platform> <contest_id>")
        print("  <platform>: 'cf' for Codeforces, 'ac' for AtCoder")
        sys.exit(1)

    platform_shortcut = sys.argv[1].lower()
    contest_id = sys.argv[2]
    
    platform_map = {"cf": "codeforces", "ac": "atcoder"}
    platform = platform_map.get(platform_shortcut)
    
    if not platform:
        print(f"Error: Invalid platform shortcut '{platform_shortcut}'. Use 'cf' or 'ac'."); sys.exit(1)
    
    provider_map = {"codeforces": CodeforcesProvider, "atcoder": AtcoderProvider}
    handle = HANDLES.get(platform)
    if not handle:
        print(f"Error: Handle for '{platform}' not configured."); sys.exit(1)

    provider = provider_map[platform](platform, handle)

    print(f"\nFetching data for {platform.capitalize()} contest {contest_id}...")
    final_data = provider.fetch_data(contest_id)
    
    if final_data:
        result_markdown = Template(MARKDOWN_TEMPLATE).render(**final_data)
        filename = provider.get_filename(contest_id)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result_markdown)
        print(f"\n✅ Successfully generated markdown file: {filename}")
    else:
        print("\n❌ Failed to generate markdown file.")

if __name__ == '__main__':
    main()