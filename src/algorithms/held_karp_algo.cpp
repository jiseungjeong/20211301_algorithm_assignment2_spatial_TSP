#include "../../include/tsp_common.h"
#include "../../include/benchmark_utils.h"


int popCount(int x) {
    int count = 0;
    while(x) {
        x&=(x-1);
        count++;
    }
    return count;
}

// 전부다 float 일 필요는 없음, 노드 번호는 int여도 됨.
vector<int> solveHeldKarp(int n, vector<vector<float>> cost) {
    int S_size = pow(2, n);
    vector<vector<float>> g(S_size, vector<float>(n, INFINITY));
    vector<vector<int>> parent(S_size, vector<int>(n, -1)); // 경로 복원을 위한 parent 배열

    
    for (int k = 1; k < n; k++) {
        g[1 << k][k] = cost[0][k];
    }
    
    for (int s = 2; s < n; s++) { // 부분집합 크기
        // 크기가 s인 모든 부분집합에 대해
        for (int S = 1; S < S_size; S++) {
            if (popCount(S) != s) continue; // 크기가 s가 아니면 건너뛰기
            if (S & 1) continue; // 시작점 0을 포함하면 건너뛰기
            
            for (int k = 1; k < n; k++) {
                if (!(S & (1 << k))) continue; // k가 S에 포함되지 않으면 건너뛰기
                
                int S_without_k = S ^ (1 << k); // xor로 k 걸러내기
                
                for (int m = 1; m < n; m++) {
                    if (m == k) continue; // m != k 조건
                    if (!(S_without_k & (1 << m))) continue; // m이 S\{k}에 포함되지 않으면 건너뛰기
                    
                    float new_cost = g[S_without_k][m] + cost[m][k];
                    if (new_cost < g[S][k]) {
                        g[S][k] = new_cost;
                        parent[S][k] = m; // 경로 복원을 위해 이전 노드 기록
                    }
                }
            }
        }
    }
    
    int full_size = (1 << n) - 2; // 0번 노드를 제외한 모든 노드 (1, 2, ..., n-1)
    float min_cost = INFINITY;
    int last_node = -1;
    
    for (int k = 1; k < n; k++) {
        float final_cost = g[full_size][k] + cost[k][0]; // k에서 시작점 0으로 돌아가는 비용
        if (final_cost < min_cost) {
            min_cost = final_cost;
            last_node = k;
        }
    }
    
    // 경로 복원
    vector<int> tour;
    int current_set = full_size;
    int current_node = last_node;
    
    // 역순으로 경로 추적
    while (current_node != -1 && current_set != 0) {
        tour.push_back(current_node);
        int prev_node = parent[current_set][current_node];
        current_set = current_set ^ (1 << current_node); // 현재 노드를 집합에서 제거
        current_node = prev_node;
    }
    
    // 시작점 추가
    tour.push_back(0);
    
    // 역순이므로 뒤집기
    reverse(tour.begin(), tour.end());
    
    // 시작점으로 돌아가기
    tour.push_back(0);
    
    return tour;
}

vector<int> tspHeldKarp(const CompleteGraph& graph) {
    int n = graph.getNodeNum();

    vector<vector<float>> cost(n, vector<float>(n));
    for (int i = 0; i < n; i++){
        for (int j = 0; j < n; j++) {
            cost[i][j] = graph.getCost(i, j);
        }
    }

    vector<int> tour = solveHeldKarp(n, cost);
    return tour;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "Usage: " << argv[0] << " <tsp_file> <output_file> [csv_file]" << endl;
        return 1;
    }
    
    string tsp_filename = argv[1];
    string output_filename = argv[2];
    string csv_filename = (argc > 3) ? argv[3] : "";

    try {
        // I/O 시간 제외하고 순수 계산 시간만 측정
        CompleteGraph graph = parseTSP(tsp_filename);
        vector<pair<double, double>> coordinates = parseCoordinates(tsp_filename);
        
        BenchmarkTimer timer;
        timer.start();
        
        // 순수 TSP 계산 시간만 측정
        vector<int> tour = tspHeldKarp(graph);
        
        timer.stop();
        
        // 투어 길이 계산
        int total_distance = 0;
        for (int i = 0; i < tour.size() - 1; i++) {
            total_distance += graph.getCost(tour[i], tour[i + 1]);
        }
        
        cout << "Algorithm: Held-Karp" << endl;
        cout << "Dataset: " << tsp_filename << endl;
        cout << "Nodes: " << graph.getNodeNum() << endl;
        cout << "Execution time: " << timer.getMilliseconds() << " ms" << endl;
        cout << "Tour distance: " << total_distance << endl;
        
        // 결과 저장
        saveTourToFile(tour, coordinates, output_filename, total_distance);
        
        // CSV 저장
        if (!csv_filename.empty()) {
            string dataset_name = tsp_filename.substr(tsp_filename.find_last_of("/") + 1);
            dataset_name = dataset_name.substr(0, dataset_name.find_last_of("."));
            saveBenchmarkResult(csv_filename, "Held-Karp", dataset_name, 
                              graph.getNodeNum(), timer.getMilliseconds(), total_distance);
        }
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}