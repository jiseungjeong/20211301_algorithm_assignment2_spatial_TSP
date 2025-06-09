#include "../../include/tsp_common.h"
#include "../../include/heap_utils.h"
#include "../../include/benchmark_utils.h"
#include "../../include/ablation_study.h"
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

// Brute-force KNN 구현
vector<int> bruteForceFindKNN(const vector<Point2D>& points, int targetId, int k) {
    vector<pair<double, int>> distances;
    
    for (int i = 0; i < points.size(); i++) {
        if (i != targetId) {
            double dist = points[targetId].distance(points[i]);
            distances.push_back({dist, i});
        }
    }
    
    // 거리 기준 정렬
    sort(distances.begin(), distances.end());
    
    vector<int> result;
    for (int i = 0; i < min(k, (int)distances.size()); i++) {
        result.push_back(distances[i].second);
    }
    
    return result;
}

// Phase 1: KD-Tree를 사용한 Candidate Edge Filtering
vector<vector<int>> buildCandidateEdgesKDTree(const vector<Point2D>& points, int k, double& time_ms) {
    BenchmarkTimer timer;
    timer.start();
    
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
    
    timer.stop();
    time_ms = timer.getMilliseconds();
    
    return candidates;
}

// Phase 1: Brute-Force를 사용한 Candidate Edge Filtering
vector<vector<int>> buildCandidateEdgesBruteForce(const vector<Point2D>& points, int k, double& time_ms) {
    BenchmarkTimer timer;
    timer.start();
    
    int n = points.size();
    vector<vector<int>> candidates(n);
    
    for (int i = 0; i < n; i++) {
        vector<int> neighbors = bruteForceFindKNN(points, i, k);
        candidates[i] = neighbors;
    }
    
    timer.stop();
    time_ms = timer.getMilliseconds();
    
    return candidates;
}

// 후보 간선 개수 계산
double countCandidateEdges(const vector<vector<int>>& candidates) {
    double total = 0;
    for (const auto& candidateList : candidates) {
        total += candidateList.size();
    }
    return total / 2.0; // 중복 제거
}

// Phase 2: Greedy Insertion
vector<int> greedyInsertion(const vector<Point2D>& points, 
                           const vector<vector<int>>& candidates) {
    int n = points.size();
    vector<bool> visited(n, false);
    vector<int> tour;
    
    // 시작점 선택
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

// 투어의 총 거리 계산
double calculateTourLength(const vector<int>& tour, const vector<Point2D>& points) {
    double totalLength = 0;
    for (int i = 0; i < tour.size() - 1; i++) {
        totalLength += points[tour[i]].distance(points[tour[i + 1]]);
    }
    return totalLength;
}

// Phase 4: 2-opt Post-Processing (측정 버전)
void selective2optMeasured(vector<int>& tour, const vector<Point2D>& points, 
                          double& timeBefore, double& timeAfter, double& time_ms, int iterations = 2) {
    BenchmarkTimer timer;
    
    // 2-opt 이전 거리 측정
    timeBefore = calculateTourLength(tour, points);
    
    timer.start();
    
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
    
    timer.stop();
    time_ms = timer.getMilliseconds();
    
    // 2-opt 이후 거리 측정
    timeAfter = calculateTourLength(tour, points);
}

// Ablation Study 메인 함수
AblationStudyStats runAblationStudy(const vector<pair<double, double>>& coordinates) {
    int n = coordinates.size();
    
    // 좌표를 Point2D로 변환
    vector<Point2D> points(n);
    for (int i = 0; i < n; i++) {
        points[i] = Point2D(coordinates[i].first, coordinates[i].second, i);
    }
    
    AblationStudyStats stats;
    stats.nodes = n;
    
    BenchmarkTimer totalTimer;
    
    cout << "🔬 Starting Ablation Study for " << n << " nodes" << endl;
    
    // Phase 1 비교: KD-tree vs Brute-force
    cout << "📊 Phase 1: KD-tree vs Brute-force KNN comparison" << endl;
    
    int k = min(30, max(10, n / 10)); // 적응적 k 값
    
    totalTimer.start();
    vector<vector<int>> candidatesKDTree = buildCandidateEdgesKDTree(points, k, stats.kdtree_phase1_time_ms);
    stats.kdtree_candidate_edges = countCandidateEdges(candidatesKDTree);
    
    vector<vector<int>> candidatesBruteForce = buildCandidateEdgesBruteForce(points, k, stats.bruteforce_phase1_time_ms);
    stats.bruteforce_candidate_edges = countCandidateEdges(candidatesBruteForce);
    
    cout << "   KD-tree time: " << stats.kdtree_phase1_time_ms << " ms" << endl;
    cout << "   Brute-force time: " << stats.bruteforce_phase1_time_ms << " ms" << endl;
    cout << "   Speed-up ratio: " << (stats.bruteforce_phase1_time_ms / stats.kdtree_phase1_time_ms) << "x" << endl;
    
    // Phase 2 & 3: KD-tree 버전으로 투어 생성
    vector<int> greedyTour = greedyInsertion(points, candidatesKDTree);
    vector<int> mstTour = mstBasedTour(points, candidatesKDTree);
    
    double greedyLength = calculateTourLength(greedyTour, points);
    double mstLength = calculateTourLength(mstTour, points);
    
    vector<int> bestTour = (greedyLength < mstLength) ? greedyTour : mstTour;
    vector<int> bestTourCopy = bestTour; // 2-opt 비교용 복사본
    
    // Phase 4: 2-opt 효과 측정
    cout << "📊 Phase 4: 2-opt optimization analysis" << endl;
    
    selective2optMeasured(bestTour, points, stats.distance_before_2opt, 
                         stats.distance_after_2opt, stats.phase4_2opt_time_ms);
    
    stats.improvement_ratio_2opt = (stats.distance_before_2opt - stats.distance_after_2opt) / stats.distance_before_2opt;
    
    cout << "   Distance before 2-opt: " << stats.distance_before_2opt << endl;
    cout << "   Distance after 2-opt: " << stats.distance_after_2opt << endl;
    cout << "   2-opt improvement: " << (stats.improvement_ratio_2opt * 100) << "%" << endl;
    cout << "   2-opt time: " << stats.phase4_2opt_time_ms << " ms" << endl;
    
    totalTimer.stop();
    stats.total_time_kdtree_ms = totalTimer.getMilliseconds();
    stats.final_distance_kdtree = stats.distance_after_2opt;
    
    // Brute-force 전체 실행 (비교용)
    totalTimer.start();
    vector<int> greedyTourBF = greedyInsertion(points, candidatesBruteForce);
    vector<int> mstTourBF = mstBasedTour(points, candidatesBruteForce);
    
    double greedyLengthBF = calculateTourLength(greedyTourBF, points);
    double mstLengthBF = calculateTourLength(mstTourBF, points);
    
    vector<int> bestTourBF = (greedyLengthBF < mstLengthBF) ? greedyTourBF : mstTourBF;
    
    double dummy1, dummy2, dummy3;
    selective2optMeasured(bestTourBF, points, dummy1, dummy2, dummy3);
    
    totalTimer.stop();
    stats.total_time_bruteforce_ms = totalTimer.getMilliseconds();
    stats.final_distance_bruteforce = calculateTourLength(bestTourBF, points);
    
    // 분석 결과 계산
    stats.time_complexity_ratio = stats.bruteforce_phase1_time_ms / stats.kdtree_phase1_time_ms;
    stats.quality_difference = abs(stats.final_distance_kdtree - stats.final_distance_bruteforce) / 
                              min(stats.final_distance_kdtree, stats.final_distance_bruteforce);
    
    cout << "\n🎯 Ablation Study Summary:" << endl;
    cout << "   Time complexity ratio (BF/KD): " << stats.time_complexity_ratio << "x" << endl;
    cout << "   Quality difference: " << (stats.quality_difference * 100) << "%" << endl;
    
    return stats;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        cout << "Usage: " << argv[0] << " <tsp_file> <output_file> [ablation_csv]" << endl;
        return 1;
    }
    
    string tsp_filename = argv[1];
    string output_filename = argv[2];
    string ablation_csv = (argc > 3) ? argv[3] : "";
    
    try {
        vector<pair<double, double>> coordinates = parseCoordinates(tsp_filename);
        
        // Ablation Study 실행
        AblationStudyStats stats = runAblationStudy(coordinates);
        
        string dataset_name = tsp_filename.substr(tsp_filename.find_last_of("/") + 1);
        dataset_name = dataset_name.substr(0, dataset_name.find_last_of("."));
        stats.dataset_name = dataset_name;
        
        cout << "\nAlgorithm: Spatial-Algorithm-Ablation" << endl;
        cout << "Dataset: " << tsp_filename << endl;
        cout << "Nodes: " << coordinates.size() << endl;
        
        // 결과 저장
        // 여기서는 KD-tree 버전 결과를 저장
        vector<Point2D> points(coordinates.size());
        for (int i = 0; i < coordinates.size(); i++) {
            points[i] = Point2D(coordinates[i].first, coordinates[i].second, i);
        }
        
        // KD-tree 버전으로 최종 투어 생성
        int k = min(30, max(10, (int)coordinates.size() / 10));
        double dummy_time;
        vector<vector<int>> candidates = buildCandidateEdgesKDTree(points, k, dummy_time);
        vector<int> greedyTour = greedyInsertion(points, candidates);
        vector<int> mstTour = mstBasedTour(points, candidates);
        
        double greedyLength = calculateTourLength(greedyTour, points);
        double mstLength = calculateTourLength(mstTour, points);
        vector<int> finalTour = (greedyLength < mstLength) ? greedyTour : mstTour;
        
        double dummy1, dummy2, dummy3;
        selective2optMeasured(finalTour, points, dummy1, dummy2, dummy3);
        
        // CompleteGraph 생성하여 정수 거리로 변환
        CompleteGraph graph = parseTSP(tsp_filename);
        int total_distance = 0;
        for (int i = 0; i < finalTour.size() - 1; i++) {
            total_distance += graph.getCost(finalTour[i], finalTour[i + 1]);
        }
        
        saveTourToFile(finalTour, coordinates, output_filename, total_distance);
        
        // Ablation study 결과 저장
        if (!ablation_csv.empty()) {
            ifstream test_file(ablation_csv);
            bool file_exists = test_file.good();
            test_file.close();
            
            if (!file_exists) {
                initAblationStatsCSV(ablation_csv);
            }
            
            saveAblationStats(ablation_csv, stats);
        }
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
} 