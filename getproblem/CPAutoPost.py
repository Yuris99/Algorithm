import requests
from jinja2 import Template
from datetime import datetime

# ==================================================================
# 사용자 설정 (USER CONFIG)
# ==================================================================
HANDLE = "Yuris" 
# ==================================================================


# 마크다운 템플릿
MARKDOWN_TEMPLATE = """
---
title: {{ contest.title }}
categories: Codeforces
tags: codeforces cf_summary
article_header:
  type: cover
---
## Contest info

[> Go to Codeforces Contests list](../codeforces)

| Title | <a href="{{ contest.link }}">{{ contest.title_short }}</a> |
| Division | {{ contest.division }} |
| Date | {{ contest.date }} |
| Official | {{ "Rated" if player.is_rated else "Unrated" }} |
| Rank | {{ player.rank }} |
| Performance | <strong><span style="color:#0000FF">1652</span></strong> |
| Rating | <strong><span style="color:{{ player.rating_color }}">{{ player.new_rating }}</span></strong>  <span style="color:#777777">({{ player.rating_change_str }})</span> |

## Problems

| <strong>#</strong> | <strong>Name</strong> | <strong> Solved </strong> | <strong>Attempt</strong> |
| :---: | --- | :---: | :---: |
{% for problem in problems %}
| {{ problem.index }} | {{ problem.name }} | {{ problem.status_html }} | {{ problem.attempts }} |
{%- endfor %}


## Solution
{% for problem in problems %}
### {{ problem.index }}. {{ problem.name }}
#### 요약

##### 제한

#### 풀이

{% endfor %}
"""

def get_rating_color(rating):
    """레이팅에 따라 색상을 반환하는 함수"""
    if rating < 1200: return "#808080"  # Gray
    if rating < 1400: return "#478000"  # Green
    if rating < 1600: return "#77DDBB"  # Cyan (Mint)
    if rating < 1900: return "#0000FF"  # Blue
    if rating < 2100: return "#AA00AA"  # Violet
    if rating < 2400: return "#FF8C00"  # Orange
    return "#FF0000"  # Red

def call_cf_api(method, params):
    """Codeforces API를 호출하는 함수"""
    url = f"https://codeforces.com/api/{method}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == 'OK':
            return data['result']
        else:
            print(f"API Error: {data.get('comment', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    platform = input("Enter platform (codeforces): ").strip().lower()
    if platform != 'codeforces':
        print("Sorry, only 'codeforces' is supported.")
        return

    contest_id = input("Enter contest ID: ").strip()

    print(f"\nFetching data for Codeforces contest {contest_id} for user {HANDLE}...")

    # 1. 대회 정보 및 문제 목록 가져오기
    standings_data = call_cf_api('contest.standings', {'contestId': contest_id, 'handles': HANDLE, 'showUnofficial': 'true'})
    if not standings_data:
        return

    contest_info = standings_data['contest']
    problems_list = standings_data['problems']
    user_row = standings_data['rows'][0] if standings_data['rows'] else None

    # 2. 레이팅 변화 정보 가져오기
    rating_changes_data = call_cf_api('contest.ratingChanges', {'contestId': contest_id})
    user_rating = None
    if rating_changes_data:
        for change in rating_changes_data:
            if change['handle'] == HANDLE:
                user_rating = change
                break
    
    # 3. 유저의 모든 제출 기록 가져오기 (업솔빙 확인용)
    user_status_data = call_cf_api('user.status', {'handle': HANDLE})
    
    # 데이터 가공
    # Contest 데이터
    contest_date = datetime.fromtimestamp(contest_info['startTimeSeconds']).strftime('%Y / %m / %d')
    division = ''.join(c for c in contest_info['name'] if 'Div' in c or c.isdigit()).replace("Div.", "Div. ")
    
    contest_data = {
        'title': contest_info['name'],
        'title_short': contest_info['name'].replace(f"({division})", "").strip(),
        'division': division if division else "N/A",
        'date': contest_date,
        'link': f"https://codeforces.com/contest/{contest_id}",
    }

    # Player 데이터
    player_data = {}
    if user_rating:
        change = user_rating['newRating'] - user_rating['oldRating']
        player_data = {
            'rank': user_rating['rank'],
            'new_rating': user_rating['newRating'],
            'rating_change_str': f"+{change}" if change >= 0 else str(change),
            'rating_color': get_rating_color(user_rating['newRating']),
            'is_rated': True
        }
    elif user_row: # Unrated 참가
        player_data = {
            'rank': user_row['rank'],
            'new_rating': 'N/A',
            'rating_change_str': 'N/A',
            'rating_color': '#000000',
            'is_rated': False
        }
    else: # 참가 안함
        player_data = { 'rank': 'N/A', 'new_rating': 'N/A', 'rating_change_str': 'N/A', 'rating_color': '#000000', 'is_rated': False }


    # Problems 데이터
    problems_data = []
    contest_end_time = contest_info['startTimeSeconds'] + contest_info.get('durationSeconds', 0)

    for prob in problems_list:
        p_data = {
            'index': prob['index'],
            'name': prob['name'],
            'status_html': '',
            'attempts': 0
        }
        
        # 대회 중 해결 여부
        solved_in_contest = False
        if user_row:
            problem_result = user_row['problemResults'][problems_list.index(prob)]
            p_data['attempts'] = problem_result['rejectedAttemptCount']
            if problem_result['points'] > 0:
                p_data['status_html'] = '<span style="color:green"> solved </span>'
                solved_in_contest = True
        
        # 업솔빙 여부 (대회 중 못 풀었을 경우에만 확인)
        if not solved_in_contest and user_status_data:
            for submission in user_status_data:
                if (submission['problem']['contestId'] == int(contest_id) and 
                    submission['problem']['index'] == prob['index'] and
                    submission['verdict'] == 'OK' and
                    submission['creationTimeSeconds'] > contest_end_time):
                    p_data['status_html'] = '<span style="color:orange"> upsolved </span>'
                    break

        problems_data.append(p_data)

    # 템플릿 렌더링
    template = Template(MARKDOWN_TEMPLATE)
    result_markdown = template.render(
        contest=contest_data,
        player=player_data,
        problems=problems_data
    )
    
    # 파일로 저장
    filename = f"{contest_id}_{HANDLE}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result_markdown)
        
    print(f"\n✅ Successfully generated markdown file: {filename}")


if __name__ == '__main__':
    main()