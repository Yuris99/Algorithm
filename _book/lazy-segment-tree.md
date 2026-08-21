---
title: Lazy Segment Tree (느리게 갱신되는 세그먼트 트리)
categories: docs
tags: algorithm, segment_tree, lazy_propagation
---

# 레이지 세그먼트 트리

구간 업데이트가 자주 일어날 때 사용하는 방법

쿼리가 호출될 때 쿼리에서 필요한 데이터만 한번에 업데이트하는 방식

(코드오류나면 말해주세요)

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

//1-base 최댓값 세그먼트트리
struct segtree {
    vector<int> tree;
    vector<int> lazy;
    int n;

    segtree(int N) {
        n = N;
        tree.resize(n*4);
        lazy.resize(n*4);
    }

    //구간 업데이트 내부 순환 코드
    //l~r: 현재 노드가 포함하고 있는 구간
    void update(int now, int l, int r, int s, int e, int v) {
        //업데이트할게 남아있으면 갱신
        lazy_update(now, l, r);

        //만약 현재 노드 구간이 전혀 포함하지 않으면 리턴
        if(r < s || e < l) return;
        //만약 현재 노드 구간이 구하고 싶은 구간 안에 있으면
        if(s <= l && r <= e) {
            tree[now] += v;
            //리프노드가 아니라면 자식 레이지 업데이트
            if(l!=r) {
                lazy[now*2]+=v;
                lazy[now*2+1]+=v;
            }
            return;
        }
        //자식 업데이트
        int m = (l+r)/2;
        update(now*2, l, m, s, e, v);
        update(now*2+1, m+1, r, s, e, v);

        tree[now] = tree[now*2] + tree[now*2+1]; //자식 노드 합 갱신
    }
    //구간 업데이트 (+v)
    void update(int s, int e, int v) {
        update(1, 1, n, s, e, v);
    }

    //레이지를 갱신하는 함수
    void lazy_update(int now, int l, int r) {
        //미뤄뒀던 업데이트 적용, 자식노드 전체를 갱신하기 때문에 구간만큼 곱해줌
        tree[now] += lazy[now]*(r-l+1);
        //리프노드가 아니면 자식한테 전파
        if(l != r) {
            lazy[now*2] += lazy[now];
            lazy[now*2+1] += lazy[now];
        }
        //초기화
        lazy[now] = 0;
    }

    //구간합을 가져오는 쿼리
    int query(int now, int l, int r, int s, int e) {
        //현재 구간에 갱신하지 않은 값이 남아있으면 업데이트
        lazy_update(now, l, r);
        //만약 현재 노드 구간이 구하고 싶은 구간 안에 있으면
        if(s <= l && r <= e) return tree[now];
        //만약 현재 노드 구간이 전혀 포함하지 않으면
        if(r < s || e < l) return -1e9;

        //아니면 자식 합을 가져옴
        int m = (l+r)/2;
        return query(now*2, l, m, s, e) + query(now*2+1, m+1, r, s, e);
    }
    //구간 합을 가져오는 쿼리
    int query(int s, int e) {
        return query(1, 1, n, s, e);
    }
};
```

[기본 세그먼트 트리로 돌아가기]({{ '/book/segment-tree/' | relative_url }})
