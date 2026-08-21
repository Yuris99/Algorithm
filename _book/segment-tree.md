---
title: Segment Tree (구간 트리)
categories: docs
tags: algorithm, segment_tree
---


# 세그먼트 트리

## 개념

특정 구간을 탐색할 때 사용하는 알고리즘.

구간 탐색을 여러번 반복할 때 주로 사용

알아두면 자주 쓰인다 

**시간복잡도:**

- 갱신: $\text{O(logN)}$
- 탐색: $\text{O(logN)}$

탑다운 기준으로, tree index를 1부터 시작하여 자식노드를 탐색한다.

이진 트리 형태로, 자식 노드는 각각 현재 노드의 왼쪽 절반과 오른쪽 절반을 포함하고 있다.

![](/assets/images/Docs/SegmentTreeGraph.png)       

## 구현

### 탑 다운 세그먼트 트리

![](/assets/images/Docs/SegmentTreeGraph1.png)      

탑다운 세그먼트 트리는 주로 재귀함수로 구현한다.

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

//1-base 최댓값 세그먼트트리
struct segtree {
    vector<int> tree;
    int n;

    segtree(int N) {
        n = N;
        tree.resize(n*4);
    }

    //단일값 업데이트 내부 순환 코드
    //l~r: 현재 노드가 포함하고 있는 구간
    void update(int now, int l, int r, int i, int v) {
        if(l==r) { 
            //하나의 요소만 담고 있는 노드 == 리프노드
            tree[now] = v;
            return;
        }
        //리프노드가 아닐 떄
        int m = (l+r)/2; //이분탐색 mid
        if(i <= m) update(now*2, l, m, i, v); //왼쪽 절반 탐색; 
        else update(now*2+1, m+1, r, i, v); //오른쪽 절반 탐색;
        
        tree[now] = max(tree[now*2], tree[now*2+1]); //자식 노드 최댓값 갱신
    }
    //단일값 업데이트 
    void update(int i, int v) {
        update(1, 1, n, i, v);
    }

    //구간 최댓값을 가져오는 쿼리
    int query(int now, int l, int r, int s, int e) {
        //만약 현재 노드 구간이 구하고 싶은 구간 안에 있으면
        if(s <= l && r <= e) return tree[now];
        //만약 현재 노드 구간이 전혀 포함하지 않으면
        if(r < s || e < l) return -1e9;
        
        //아니면 자식의 최댓값을 가져옴
        int m = (l+r)/2;
        return max(query(now*2, l, m, s, e), query(now*2+1, m+1, r, s, e));
    }
    //구간 최댓값을 가져오는 쿼리
    int query(int s, int e) {
        return query(1, 1, n, s, e);
    }
};
```

### 바텀 업 세그먼트 트리

비트연산을 사용한 세그먼트 트리.

직관적이진 않지만 코드가 짧고 빠르다

2*n을 초과할 일이 없기 때문에 메모리 선언이 안전하다

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

//0-base 최댓값 세그먼트트리
struct segtree {
    vector<int> tree;
    int n;

    segtree(int N) {
        n = N;
        tree.resize(2*n);
    }

    void update(int i, int v) {
        //리프노드부터 시작
        i += n;
        tree[i] = v;

        //부모노드를 갱신
        for(; i >= 1; i >>= 1) tree[i >> 1] = max(tree[i], tree[i^1]);
    }
    //s~e 구간 최댓값을 가져오는 쿼리
    int query(int s, int e) {
        //s와 e의 리프노드 탐색.
        //연산을 편하게 하기 위해 [s, e)범위로 잡는다
        s += n;
        e += n+1;
        int ret = -1e9;

        //s==e까지 (서로 만날때 까지, 루트)
        for(; s < e; s >>= 1, e >>= 1) {
            //s가 홀수 (오른쪽 노드)라면? 부모는 왼쪽 노드를 포함하고 있기 때문에 현재 노드만 계산
            if(s & 1) ret = max(ret, tree[s++]);
            //e가 홀수 (오른쪽 노드)라면? e는 open이기 때문에 포함되면 안되서 내 왼쪽 노드만 계산
            if(e & 1) ret = max(ret, tree[--e]);
        }
        return ret;
    }
};
```

## 파생 자료구조

- [레이지 세그먼트 트리]({{ '/book/lazy-segment-tree/' | relative_url }}): 구간 갱신을 느리게 전파하는 세그먼트 트리
- [펜윅 트리]({{ '/book/fenwick-tree/' | relative_url }}): 누적합을 효율적으로 관리하는 트리
- [퍼시스턴트 세그먼트 트리]({{ '/book/persistent-segment-tree/' | relative_url }}): 갱신 이전 버전을 보존하는 세그먼트 트리
