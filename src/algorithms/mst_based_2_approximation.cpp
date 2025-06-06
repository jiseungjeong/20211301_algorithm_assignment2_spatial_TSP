#include "../../include/tsp_common.h"
#include "../../include/heap_utils.h"

// DFS를 통한 MST preorder traversal
void dfs(int u, const vector<vector<int> >& mst, vector<bool>& visited, vector<int>& tour) {
    visited[u] = true;
    tour.push_back(u);

    for (int i = 0; i < mst[u].size(); i++) {
        int v = mst[u][i];
        if (!visited[v]) {
            dfs(v, mst, visited, tour);
        }
    }
}

// Priority Queue 기반 Prim 알고리즘으로 MST 구축
vector<vector<int> > buildMST(const CompleteGraph& graph, int root) {
    int n = graph.getNodeNum();
    vector<vector<int> > mst(n);
    vector<int> parent(n, -1);
    vector<bool> in_mst(n, false);
    vector<int> key(n, INT_MAX);
    
    PQNodeInt* pq = new PQNodeInt[n];
    int pq_size = n;
    

    // priority 큐 초기화
    for (int i = 0; i < n; i++) {
        pq[i] = PQNodeInt(i, INT_MAX);
        key[i] = INT_MAX;
    }
    
    pq[root].key = 0;
    key[root] = 0;
    
    build_min_heap_int(pq, pq_size);
    
    while (pq_size > 0) {
        PQNodeInt min_node = extract_min_int(pq, pq_size);
        int u = min_node.vertex;
        
        if (min_node.key == INT_MAX) {
            break;
        }
        
        in_mst[u] = true;
        
        for (int v = 0; v < n; v++) {
            if (!in_mst[v]) {
                int cost = graph.getCost(u, v);
                if (cost > 0 && cost < key[v]) {
                    key[v] = cost;
                    parent[v] = u;
                    decrease_key_int(pq, pq_size, v, cost);
                }
            }
        }
    }
    
    // MST 인접 리스트 구성
    for (int i = 0; i < n; i++) {
        if (parent[i] != -1) {
            mst[parent[i]].push_back(i);
            mst[i].push_back(parent[i]);
        }
    }
    
    delete[] pq;
    return mst;
}

// TSP 2-Approximation 알고리즘
vector<int> tsp2Approximation(const CompleteGraph& graph) {
    int n = graph.getNodeNum();
    int root = 0;

    // 1. MST 구축
    vector<vector<int> > mst = buildMST(graph, root);

    // 2. DFS 전위 순회
    vector<bool> visited(n, false);
    vector<int> tour;
    dfs(root, mst, visited, tour);

    // 3. 시작점으로 돌아가기
    tour.push_back(root);

    return tour;
}

int main(int argc, char* argv[]) {
    string tsp_filename = argv[1];
    string output_filename = argv[2];
    
    // 템플릿 함수를 사용해서 TSP 2-approximation 실행
    solveTSPWithAlgorithm(tsp_filename, output_filename, tsp2Approximation);
    
    return 0;
}