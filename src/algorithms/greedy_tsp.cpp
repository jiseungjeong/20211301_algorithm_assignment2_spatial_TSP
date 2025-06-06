#include "../../include/tsp_common.h"

// Greedy TSP 알고리즘 (Nearest Neighbor)
vector<int> greedyTSP(const CompleteGraph& graph) {
    int n = graph.getNodeNum();
    vector<bool> visited(n, false);
    vector<int> tour;
    
    // 시작점은 0번 노드
    int current = 0;
    tour.push_back(current);
    visited[current] = true;
    
    // 모든 노드를 방문할 때까지 반복
    for (int step = 1; step < n; step++) {
        int next = -1;
        int min_distance = INT_MAX;
        
        // 현재 노드에서 가장 가까운 미방문 노드 찾기
        for (int i = 0; i < n; i++) {
            if (!visited[i]) {
                int distance = graph.getCost(current, i);
                if (distance < min_distance) {
                    min_distance = distance;
                    next = i;
                }
            }
        }
        
        // 다음 노드로 이동
        if (next != -1) {
            tour.push_back(next);
            visited[next] = true;
            current = next;
        }
    }
    
    // 시작점으로 돌아가기
    tour.push_back(0);
    
    return tour;
}

int main(int argc, char* argv[]) {
    string tsp_filename = argv[1];
    string output_filename = argv[2];
    
    // 템플릿 함수를 사용해서 Greedy TSP 실행
    solveTSPWithAlgorithm(tsp_filename, output_filename, greedyTSP);
    
    return 0;
} 