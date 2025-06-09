#include "../../include/tsp_common.h"
#include "../../include/heap_utils.h"
#include "../../include/benchmark_utils.h"

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
        vector<int> tour = tsp2Approximation(graph);
        
        timer.stop();
        
        // 투어 길이 계산
        int total_distance = 0;
        for (int i = 0; i < tour.size() - 1; i++) {
            total_distance += graph.getCost(tour[i], tour[i + 1]);
        }
        
        cout << "Algorithm: MST-2-Approximation" << endl;
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
            saveBenchmarkResult(csv_filename, "MST-2-Approximation", dataset_name, 
                              graph.getNodeNum(), timer.getMilliseconds(), total_distance);
        }
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}