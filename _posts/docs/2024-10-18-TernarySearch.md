---
title: Ternary Search (삼분 탐색)
categories: docs
tags: algorithm, binary_search
article_header:
  type: cover
---


이분 탐색은 mid를 기준으로 Left와 Right로 나누었다면, 삼분 탐색은 Left, mid, Right **3개로 구간을 나누는 방식**이다. 
삼분탐색은 데이터의 분포가 Unimodal한 데이터에서 사용 가능하다. (아래 그래프 참조)    
> Unimodal function?       
하나의 극값을 가지는 함수     

![](/assets/images/Docs/TernarySearchGraph.png)       
Left, mid1, mid2, Right함수를 가지고 시작한다.        
m1이 m2보다 크다면, 데이터가 오른쪽편에 있다는 뜻이므로 Left를 m1으로 바꾼다.       
M2가 m1보다 크다면, 데이터가 왼쪽편에 있다는 뜻이므로 Right를 m2로 바꾼다.        
이런 식으로 데이터의 범위를 줄여가며 l+3 <= r이 될 때 까지 탐색한다.        
그 이후 l부터 r까지 3개 이하의 데이터를 탐색해보면 정답을 찾을 수 있다.       
이런 형태로 $O(n\log{n})$의 시간복잡도 안에 탐색을 할 수 있다.


# Example
## 전봇대 (BOJ 8986)
https://www.acmicpc.net/problem/8986      
삼분탐색의 가장 대표적인 문제이다. 전봇대 사이의 거리를 x라고 잡고, 각각 데이터를 출력해보면 Unimodal하다는 사실을 알수 있다.