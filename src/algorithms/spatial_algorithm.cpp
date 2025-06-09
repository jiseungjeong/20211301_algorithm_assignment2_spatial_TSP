#include "../../include/tsp_common.h"
#include "../../include/heap_utils.h"
#include "../../include/benchmark_utils.h"
#include "../../include/spatial_analysis.h"
#include <algorithm>
#include <set>
#include <ctime>

// 2D 점 구조체
struct Point2D {
    double x, y;
    int id;
    
    Point2D() : x(0), y(0), id(-1) {}
    Point2D(double x, double y, int id) : x(x), y(y), id(id) {}
    
    double distance(const Point2D& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        return sqrt(dx * dx + dy * dy);
    }
};

// KD-Tree 노드
struct KDNode {
    Point2D point;
    KDNode* left;
    KDNode* right;
    int depth;
    
    KDNode(const Point2D& p, int d) : point(p), left(nullptr), right(nullptr), depth(d) {}
};

// KD-Tree 클래스
class KDTree {
private:
    KDNode* root;
    
    KDNode* buildTree(vector<Point2D>& points, int depth) {
        if (points.empty()) return nullptr;
        
        int axis = depth % 2; // 0: x축, 1: y축
        
        // 현재 축을 기준으로 정렬
        sort(points.begin(), points.end(), [axis](const Point2D& a, const Point2D& b) {
            return (axis == 0) ? a.x < b.x : a.y < b.y;
        });
        
        int median = points.size() / 2;
        KDNode* node = new KDNode(points[median], depth);
        
        vector<Point2D> leftPoints(points.begin(), points.begin() + median);
        vector<Point2D> rightPoints(points.begin() + median + 1, points.end());
        
        node->left = buildTree(leftPoints, depth + 1);
        node->right = buildTree(rightPoints, depth + 1);
        
        return node;
    }
    
    void knnSearch(KDNode* node, const Point2D& target, int k, 
                   DistNode* nearest, int& heap_size) {
        if (!node) return;
        
        double dist = target.distance(node->point);
        
        // max-heap을 사용한 k-nearest neighbor
        insert_max_heap(nearest, heap_size, k, DistNode(dist, node->point.id));
        
        int axis = node->depth % 2;
        double targetAxis = (axis == 0) ? target.x : target.y;
        double nodeAxis = (axis == 0) ? node->point.x : node->point.y;
        
        KDNode* first = (targetAxis < nodeAxis) ? node->left : node->right;
        KDNode* second = (targetAxis < nodeAxis) ? node->right : node->left;
        
        knnSearch(first, target, k, nearest, heap_size);
        
        // 다른 쪽도 확인할 필요가 있는지 판단
        if (heap_size < k || abs(targetAxis - nodeAxis) < nearest[0].dist) {
            knnSearch(second, target, k, nearest, heap_size);
        }
    }
    
public:
    KDTree(vector<Point2D> points) {
        root = buildTree(points, 0);
    }
    
    vector<int> findKNN(const Point2D& target, int k) {
        DistNode* nearest = new DistNode[k];
        int heap_size = 0;
        
        knnSearch(root, target, k, nearest, heap_size);
        
        vector<int> result;
        for (int i = 0; i < heap_size; i++) {
            result.push_back(nearest[i].id);
        }
        
        delete[] nearest;
        return result;
    }
};

// Phase 1: Candidate Edge Filtering
vector<vector<int>> buildCandidateEdges(const vector<Point2D>& points, int k = 20) {
    cout << "Phase 1: Building candidate edges with k=" << k << endl;
    
    vector<Point2D> pointsCopy = points;
    KDTree kdTree(pointsCopy);
    
    int n = points.size();
    vector<vector<int>> candidates(n);
    
    for (int i = 0; i < n; i++) {
        vector<int> neighbors = kdTree.findKNN(points[i], k + 1); // +1 because it includes itself
        
        for (int neighbor : neighbors) {
            if (neighbor != i) {
                candidates[i].push_back(neighbor);
            }
        }
    }
    
    return candidates;
}

// Phase 2: Greedy Insertion
vector<int> greedyInsertion(const vector<Point2D>& points, 
                           const vector<vector<int>>& candidates) {
    cout << "Phase 2: Greedy insertion" << endl;
    
    int n = points.size();
    vector<bool> visited(n, false);
    vector<int> tour;
    
    // 시작점 선택 (중앙에 가까운 점)
    int start = 0;
    tour.push_back(start);
    visited[start] = true;
    
    for (int step = 1; step < n; step++) {
        int current = tour.back();
        int next = -1;
        double minDist = INFINITY;
        
        // 현재 점의 후보 이웃들 중에서 가장 가까운 미방문 점 찾기
        for (int candidate : candidates[current]) {
            if (!visited[candidate]) {
                double dist = points[current].distance(points[candidate]);
                if (dist < minDist) {
                    minDist = dist;
                    next = candidate;
                }
            }
        }
        
        // 후보에서 찾지 못했으면 전체에서 가장 가까운 점 찾기
        if (next == -1) {
            for (int i = 0; i < n; i++) {
                if (!visited[i]) {
                    double dist = points[current].distance(points[i]);
                    if (dist < minDist) {
                        minDist = dist;
                        next = i;
                    }
                }
            }
        }
        
        if (next != -1) {
            tour.push_back(next);
            visited[next] = true;
        }
    }
    
    tour.push_back(start); // 시작점으로 돌아가기
    return tour;
}

// Phase 3: MST-Based Correction
vector<int> mstBasedTour(const vector<Point2D>& points, 
                        const vector<vector<int>>& candidates) {
    cout << "Phase 3: MST-based correction" << endl;
    
    int n = points.size();
    vector<vector<pair<int, double>>> mstAdj(n);
    
    // Prim's algorithm로 MST 구축 (candidate edges만 사용)
    vector<bool> inMST(n, false);
    vector<double> key(n, INFINITY);
    vector<int> parent(n, -1);
    
    PQNode* pq = new PQNode[n];
    int pq_size = n;
    
    // priority 큐 초기화
    for (int i = 0; i < n; i++) {
        pq[i] = PQNode(i, INFINITY);
        key[i] = INFINITY;
    }
    
    pq[0].key = 0;
    key[0] = 0;
    
    build_min_heap(pq, pq_size);
    
    while (pq_size > 0) {
        PQNode min_node = extract_min(pq, pq_size);
        int u = min_node.vertex;
        
        if (min_node.key == INFINITY) {
            break;
        }
        
        inMST[u] = true;
        
        // 후보 이웃들 확인
        for (int v : candidates[u]) {
            if (!inMST[v]) {
                double weight = points[u].distance(points[v]);
                if (weight < key[v]) {
                    key[v] = weight;
                    parent[v] = u;
                    decrease_key(pq, pq_size, v, weight);
                }
            }
        }
    }
    
    delete[] pq;
    
    // MST 인접 리스트 구성
    for (int i = 1; i < n; i++) {
        if (parent[i] != -1) {
            mstAdj[parent[i]].push_back({i, key[i]});
            mstAdj[i].push_back({parent[i], key[i]});
        }
    }
    
    // DFS로 MST traversal
    vector<int> mstTour;
    vector<bool> visited(n, false);
    
    function<void(int)> dfs = [&](int u) {
        visited[u] = true;
        mstTour.push_back(u);
        
        for (auto& edge : mstAdj[u]) {
            int v = edge.first;
            if (!visited[v]) {
                dfs(v);
            }
        }
    };
    
    dfs(0);
    mstTour.push_back(0); // 시작점으로 돌아가기
    
    return mstTour;
}

// Phase 4: Selective 2-opt Post-Processing
void selective2opt(vector<int>& tour, const vector<Point2D>& points, int iterations = 2) {
    cout << "Phase 4: Selective 2-opt improvement" << endl;
    
    int n = tour.size() - 1; // 마지막은 시작점으로 돌아가는 것
    
    for (int iter = 0; iter < iterations; iter++) {
        // 가장 긴 간선들의 인덱스 찾기
        vector<pair<double, int>> edgeLengths;
        for (int i = 0; i < n; i++) {
            int from = tour[i];
            int to = tour[i + 1];
            double length = points[from].distance(points[to]);
            edgeLengths.push_back({length, i});
        }
        
        sort(edgeLengths.rbegin(), edgeLengths.rend()); // 내림차순 정렬
        
        // 상위 20%의 간선에 대해 2-opt 시도
        int numEdgesToCheck = max(1, n / 5);
        bool improved = false;
        
        for (int e = 0; e < numEdgesToCheck; e++) {
            int i = edgeLengths[e].second;
            
            for (int j = i + 2; j < n; j++) {
                if (j == n - 1 && i == 0) continue; // 같은 간선
                
                // 현재 거리
                double dist1 = points[tour[i]].distance(points[tour[i + 1]]) +
                              points[tour[j]].distance(points[tour[j + 1]]);
                
                // 2-opt 교환 후 거리
                double dist2 = points[tour[i]].distance(points[tour[j]]) +
                              points[tour[i + 1]].distance(points[tour[j + 1]]);
                
                if (dist2 < dist1) {
                    // 2-opt 교환 수행
                    reverse(tour.begin() + i + 1, tour.begin() + j + 1);
                    improved = true;
                    break;
                }
            }
            if (improved) break;
        }
        
        if (!improved) break;
    }
}

// 투어의 총 거리 계산
double calculateTourLength(const vector<int>& tour, const vector<Point2D>& points) {
    double totalLength = 0;
    for (int i = 0; i < tour.size() - 1; i++) {
        totalLength += points[tour[i]].distance(points[tour[i + 1]]);
    }
    return totalLength;
}

// 메인 Spatial TSP 알고리즘
vector<int> spatialTSP(const CompleteGraph& graph) {
    int n = graph.getNodeNum();
    
    // 좌표 정보가 필요하므로 임시로 그리드 형태로 생성
    vector<Point2D> points(n);
    for (int i = 0; i < n; i++) {
        // 간단한 그리드 배치 (실제로는 파일에서 읽어와야 함)
        int gridSize = (int)sqrt(n) + 1;
        points[i] = Point2D(i % gridSize, i / gridSize, i);
    }
    
    cout << "Starting Spatial TSP Algorithm for " << n << " nodes" << endl;
    
    // Phase 1: Candidate Edge Filtering
    int k = min(30, max(10, n / 10)); // 적응적 k 값
    vector<vector<int>> candidates = buildCandidateEdges(points, k);
    
    // Phase 2: Greedy Insertion
    vector<int> greedyTour = greedyInsertion(points, candidates);
    double greedyLength = calculateTourLength(greedyTour, points);
    cout << "Greedy tour length: " << greedyLength << endl;
    
    // Phase 3: MST-Based Correction
    vector<int> mstTour = mstBasedTour(points, candidates);
    double mstLength = calculateTourLength(mstTour, points);
    cout << "MST tour length: " << mstLength << endl;
    
    // 더 나은 투어 선택
    vector<int> bestTour = (greedyLength < mstLength) ? greedyTour : mstTour;
    cout << "Selected tour length: " << min(greedyLength, mstLength) << endl;
    
    // Phase 4: Selective 2-opt Post-Processing
    selective2opt(bestTour, points);
    double finalLength = calculateTourLength(bestTour, points);
    cout << "Final optimized tour length: " << finalLength << endl;
    
    return bestTour;
}

// 실제 좌표를 사용하는 버전 (분석 기능 포함)
vector<int> spatialTSPWithCoordsAnalysis(const vector<pair<double, double>>& coordinates, SpatialStats& stats) {
    int n = coordinates.size();
    
    // 좌표를 Point2D로 변환
    vector<Point2D> points(n);
    for (int i = 0; i < n; i++) {
        points[i] = Point2D(coordinates[i].first, coordinates[i].second, i);
    }
    
    cout << "Starting Spatial TSP Algorithm for " << n << " nodes with detailed analysis" << endl;
    
    BenchmarkTimer phaseTimer;
    
    // Phase 1: Candidate Edge Filtering
    phaseTimer.start();
    int k = min(30, max(10, n / 10)); 
    vector<vector<int>> candidates = buildCandidateEdges(points, k);
    phaseTimer.stop();
    stats.phase1_time_ms = phaseTimer.getMilliseconds();
    
    // Phase 2: Greedy Insertion  
    phaseTimer.start();
    vector<int> greedyTour = greedyInsertion(points, candidates);
    phaseTimer.stop();
    stats.phase2_time_ms = phaseTimer.getMilliseconds();
    double greedyLength = calculateTourLength(greedyTour, points);
    cout << "Greedy tour length: " << greedyLength << endl;
    
    // Phase 3: MST-Based Correction
    phaseTimer.start();
    vector<int> mstTour = mstBasedTour(points, candidates);
    phaseTimer.stop();
    stats.phase3_time_ms = phaseTimer.getMilliseconds();
    double mstLength = calculateTourLength(mstTour, points);
    cout << "MST tour length: " << mstLength << endl;
    
    // 통계 기록
    stats.greedy_distance = greedyLength;
    stats.mst_distance = mstLength;
    stats.greedy_only_distance = greedyLength;
    stats.mst_only_distance = mstLength;
    
    // 더 나은 투어 선택
    vector<int> bestTour = (greedyLength < mstLength) ? greedyTour : mstTour;
    double selectedLength = min(greedyLength, mstLength);
    
    if (greedyLength < mstLength) {
        stats.winner = "Greedy";
        stats.improvement_ratio = (mstLength - greedyLength) / mstLength;
        cout << "Selected: Greedy (better by " << (mstLength - greedyLength) << ")" << endl;
    } else {
        stats.winner = "MST";
        stats.improvement_ratio = (greedyLength - mstLength) / greedyLength;
        cout << "Selected: MST (better by " << (greedyLength - mstLength) << ")" << endl;
    }
    
    // Phase 4: Selective 2-opt Post-Processing
    phaseTimer.start();
    selective2opt(bestTour, points);
    phaseTimer.stop();
    stats.phase4_time_ms = phaseTimer.getMilliseconds();
    double finalLength = calculateTourLength(bestTour, points);
    cout << "Final optimized tour length: " << finalLength << endl;
    
    stats.final_distance = finalLength;
    stats.total_time_ms = stats.phase1_time_ms + stats.phase2_time_ms + 
                          stats.phase3_time_ms + stats.phase4_time_ms;
    
    cout << "\n=== PHASE ANALYSIS ===" << endl;
    cout << "Phase 1 (Candidate Filtering): " << stats.phase1_time_ms << " ms" << endl;
    cout << "Phase 2 (Greedy Insertion): " << stats.phase2_time_ms << " ms" << endl;
    cout << "Phase 3 (MST Construction): " << stats.phase3_time_ms << " ms" << endl;
    cout << "Phase 4 (2-opt Optimization): " << stats.phase4_time_ms << " ms" << endl;
    cout << "Total: " << stats.total_time_ms << " ms" << endl;
    
    return bestTour;
}

// 기존 spatialTSPWithCoords 함수 (호환성 유지)
vector<int> spatialTSPWithCoords(const vector<pair<double, double>>& coordinates) {
    SpatialStats dummy_stats;
    return spatialTSPWithCoordsAnalysis(coordinates, dummy_stats);
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "Usage: " << argv[0] << " <tsp_file> <output_file> [csv_file] [analysis_csv]" << endl;
        return 1;
    }
    
    string tsp_filename = argv[1];
    string output_filename = argv[2];
    string csv_filename = (argc > 3) ? argv[3] : "";
    string analysis_csv = (argc > 4) ? argv[4] : "";
    
    try {
        // I/O 시간 제외하고 순수 계산 시간만 측정
        vector<pair<double, double>> coordinates = parseCoordinates(tsp_filename);
        
        BenchmarkTimer timer;
        timer.start();
        
        // 분석 모드인지 확인
        SpatialStats stats;
        vector<int> tour;
        
        if (!analysis_csv.empty()) {
            // 분석 모드
            string dataset_name = tsp_filename.substr(tsp_filename.find_last_of("/") + 1);
            dataset_name = dataset_name.substr(0, dataset_name.find_last_of("."));
            stats.dataset_name = dataset_name;
            stats.nodes = coordinates.size();
            
            tour = spatialTSPWithCoordsAnalysis(coordinates, stats);
        } else {
            // 일반 모드
            tour = spatialTSPWithCoords(coordinates);
        }
        
        timer.stop();
        
        // 결과 저장을 위해 그래프도 생성
        CompleteGraph graph = parseTSP(tsp_filename);
        
        // 투어 길이 계산
        int total_distance = 0;
        for (int i = 0; i < tour.size() - 1; i++) {
            total_distance += graph.getCost(tour[i], tour[i + 1]);
        }
        
        cout << "Algorithm: Spatial-Algorithm" << endl;
        cout << "Dataset: " << tsp_filename << endl;
        cout << "Nodes: " << coordinates.size() << endl;
        cout << "Execution time: " << timer.getMilliseconds() << " ms" << endl;
        cout << "Tour distance: " << total_distance << endl;
        
        // 결과 저장
        saveTourToFile(tour, coordinates, output_filename, total_distance);
        
        // CSV 저장
        if (!csv_filename.empty()) {
            string dataset_name = tsp_filename.substr(tsp_filename.find_last_of("/") + 1);
            dataset_name = dataset_name.substr(0, dataset_name.find_last_of("."));
            saveBenchmarkResult(csv_filename, "Spatial-Algorithm", dataset_name, 
                              coordinates.size(), timer.getMilliseconds(), total_distance);
        }
        
        // 분석 결과 저장
        if (!analysis_csv.empty()) {
            // 파일이 존재하지 않으면 헤더 추가
            ifstream test_file(analysis_csv);
            bool file_exists = test_file.good();
            test_file.close();
            
            if (!file_exists) {
                initSpatialStatsCSV(analysis_csv);
            }
            
            saveSpatialStats(analysis_csv, stats);
        }
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}
