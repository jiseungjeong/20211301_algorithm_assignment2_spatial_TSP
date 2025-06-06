#ifndef TSP_COMMON_H
#define TSP_COMMON_H

#include <vector>
#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <climits>
#include <iomanip>
#include <stdexcept>

using namespace std;

int euclideanDistance(const pair<double,double>& p1, const pair<double,double>& p2);

// 완전 그래프 클래스
class CompleteGraph {
private:
    int node_num;
    vector<vector<int> > adj_mat;
    
public:
    CompleteGraph(int n);
    void addEdge(int u, int v, int cost);
    int getCost(int u, int v) const;
    int getNodeNum() const;
};

// TSP 파일 파싱 함수들
CompleteGraph parseTSP(const string& filename);
vector<pair<double,double> > parseCoordinates(const string& filename);

// 결과 저장 함수들
void saveTourToFile(const vector<int>& tour, const vector<pair<double,double> >& coordinates, 
                    const string& tour_filename, int total_distance);

// TSP 솔루션 실행 및 저장 (템플릿으로 알고리즘을 받음)
template<typename TSPAlgorithm>
void solveTSPWithAlgorithm(const string& tsp_filename, const string& output_filename, 
                          TSPAlgorithm algorithm);

// 템플릿 구현 (헤더에 포함)
template<typename TSPAlgorithm>
void solveTSPWithAlgorithm(const string& tsp_filename, const string& output_filename, TSPAlgorithm algorithm) {
    try {
        vector<pair<double,double> > coordinates = parseCoordinates(tsp_filename);
        
        // 그래프 생성
        CompleteGraph graph = parseTSP(tsp_filename);
        
        // TSP 알고리즘 수행
        vector<int> tour = algorithm(graph);
        
        // tour 길이 계산
        int total_distance = 0;
        for (int i = 0; i < (int)(tour.size() - 1); i++) {
            int from = tour[i];
            int to = tour[i + 1];
            total_distance += graph.getCost(from, to);
        }
        
        // 결과 출력
        cout << "Tour: ";
        for (int i = 0; i < min(10, (int)tour.size()); i++) {
            cout << tour[i];
            if (i < min(9, (int)tour.size() - 1)) cout << " -> ";
        }
        if (tour.size() > 10) cout << " ...";
        cout << endl;
        cout << "Total distance: " << total_distance << endl;
        
        // 파일로 저장
        saveTourToFile(tour, coordinates, output_filename, total_distance);
        
    } catch (const exception& e) {
        cout << "Error: " << e.what() << endl;
    }
}

#endif // TSP_COMMON_H 