#include "../../include/tsp_common.h"
#include "../../include/benchmark_utils.h"

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
        vector<int> tour = greedyTSP(graph);
        
        timer.stop();
        
        // 투어 길이 계산
        int total_distance = 0;
        for (int i = 0; i < tour.size() - 1; i++) {
            total_distance += graph.getCost(tour[i], tour[i + 1]);
        }
        
        cout << "Algorithm: Greedy-TSP" << endl;
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
            saveBenchmarkResult(csv_filename, "Greedy-TSP", dataset_name, 
                              graph.getNodeNum(), timer.getMilliseconds(), total_distance);
        }
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 