---
title: Sqrt Decomposition
categories: docs
tags: algorithm, sqrt_decomposition, range_query
---

# 제곱근 분할법

## 개념

세그먼트 트리와 유사한 구간 처리 기법이다.

세그먼트 트리의 쿼리 시간 복잡도는 $\text{O}(\log N)$이고, 제곱근 분할법은 $\text{O}(\sqrt{N})$이다.

![배열을 제곱근 크기의 블록으로 나눈 모습]({{ '/assets/images/Docs/SqrtDecompositionBlocks.png' | relative_url }})

먼저 배열을 약 $\sqrt{N}$ 크기의 블록으로 나누고, 각 블록의 쿼리 결과를 미리 계산한다.

구간쿼리가 들어오면, 포함되는 구간은 미리 처리해둔 쿼리를 사용하고, 나머지는 직접 계산한다.

그렇게 되면 최악의 경우에도 $2\sqrt{N}$만큼만 연산하면 쿼리를 처리할 수 있다.

![완전히 포함된 블록과 직접 계산할 양 끝 구간]({{ '/assets/images/Docs/SqrtDecompositionQuery.png' | relative_url }})

## 코드

대충 제곱근 분할법을 사용하여 구간합을 구하는 코드

```cpp
#include <iostream>
#include <vector>
#include <cmath>
using namespace std;

//Sqrt Decomposition

struct QUERY {
    int cmd;
    int l, r;
    int v;
};

vector<int> seg;
vector<int> arr;
int n;
int k;

void update(int i, int v) {
    seg[i/k]+=v;
    arr[i]+=v;
}
int query(int l, int r) {
    int ret = 0;
    while(l <= r) {
        //현재구간이 범위 안에 있으면
        if(l%k==0 && l+k-1 <= r) {
            //구간만큼 계산
            ret += seg[l/k];
            l += k;
        } else {
            //아니면 개별 데이터 계산
            ret += arr[l++];
        }
    }
    return ret;
}

//n크기의 배열에서, query 수행
//cmd 1: l에 v를 더한다.
//cmd 2: l~r사이의 합을 구한다.
void solve(int N, vector<int> a, vector<QUERY> q) {
    n = N;
    arr = a;

    k = max(1, (int)sqrt(N));
    seg.clear();
    seg.resize((n+k-1)/k, 0);
    //전처리, 제곱근만큼 나눠서 더해줌
    int now = -1;
    for(int i = 0; i < n; i++) {
        if(i%k==0) now++;
        seg[now]+=a[i];
    }
    
    //쿼리수행
    for(auto qry : q) {
        if(qry.cmd==1) update(qry.l, qry.v);
        if(qry.cmd==2) query(qry.l, qry.r);

    }
}

int main(void) {

    return 0;
}

```

## 파생 알고리즘

- [모스 알고리즘]({{ '/book/mos-algorithm/' | relative_url }}): 제곱근 분할을 이용해 오프라인 구간 쿼리의 처리 순서를 최적화한다.
