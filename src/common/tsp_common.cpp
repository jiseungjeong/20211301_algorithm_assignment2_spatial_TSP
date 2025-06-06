#include "tsp_common.h"

// 유클리드 거리 계산
int euclideanDistance(const pair<double,double>& p1, const pair<double,double>& p2) {
    double dist = sqrt(pow(p1.first - p2.first, 2) + pow(p1.second - p2.second, 2));
    return int(dist + 0.5);
}

// CompleteGraph 클래스 구현
CompleteGraph::CompleteGraph(int n) : node_num(n), adj_mat(n, vector<int>(n, 0)) {}

void CompleteGraph::addEdge(int u, int v, int cost) {
    adj_mat[u][v] = cost;
    adj_mat[v][u] = cost;
}

int CompleteGraph::getCost(int u, int v) const {
    return adj_mat[u][v];
}

int CompleteGraph::getNodeNum() const {
    return node_num;
}

// TSP 파일 파싱
CompleteGraph parseTSP(const string& filename) {
    ifstream infile(filename);
    if (!infile.is_open()) {
        throw runtime_error("Can't open the file");
    }

    string line;
    int dim = -1;
    vector<pair<double,double> > coordinates;

    while (getline(infile, line)) {
        if (line.find("DIMENSION") != string::npos) {
            size_t pos = line.find(":");
            dim = stoi(line.substr(pos+1));
            coordinates.resize(dim);
        }
        if (line.find("NODE_COORD_SECTION") != string::npos) {
            break;
        }
    }

    if (dim == -1) {
        throw runtime_error("Dimension parsing failed, -1!");
    }

    for (int i = 0; i < dim; ++i) {
        int index;
        double x, y;
        infile >> index >> x >> y;
        coordinates[index - 1] = make_pair(x, y);
    }
    infile.close();

    CompleteGraph graph(dim);
    for (int i = 0; i < dim; ++i) {
        for (int j = i + 1; j < dim; ++j) {
            int dist = euclideanDistance(coordinates[i], coordinates[j]);
            graph.addEdge(i, j, dist);
        }
    }
    
    return graph;
}

// 좌표만 파싱하는 함수
vector<pair<double,double> > parseCoordinates(const string& filename) {
    ifstream infile(filename);
    if (!infile.is_open()) {
        throw runtime_error("Can't open the file");
    }

    string line;
    int dim = -1;
    vector<pair<double,double> > coordinates;

    while (getline(infile, line)) {
        if (line.find("DIMENSION") != string::npos) {
            size_t pos = line.find(":");
            dim = stoi(line.substr(pos+1));
            coordinates.resize(dim);
        }
        if (line.find("NODE_COORD_SECTION") != string::npos) {
            break;
        }
    }

    if (dim == -1) {
        throw runtime_error("Dimension parsing failed, -1!");
    }

    for (int i = 0; i < dim; ++i) {
        int index;
        double x, y;
        infile >> index >> x >> y;
        coordinates[index - 1] = make_pair(x, y);
    }
    infile.close();

    return coordinates;
}

// tour 결과를 파일로 저장하는 함수
void saveTourToFile(const vector<int>& tour, const vector<pair<double,double> >& coordinates, 
                    const string& tour_filename, int total_distance) {
    // tour 경로 저장
    ofstream tour_file(tour_filename.c_str());
    tour_file << "# TSP Tour Result\n";
    tour_file << "# Total Distance: " << total_distance << "\n";
    tour_file << "# Tour Order:\n";
    
    for (int i = 0; i < tour.size(); i++) {
        tour_file << tour[i];
        if (i < tour.size() - 1) tour_file << " ";
    }
    tour_file << "\n";
    tour_file.close();
    
    // 좌표 데이터 저장 (실수형 좌표 지원)
    string coord_filename = tour_filename.substr(0, tour_filename.find_last_of('.')) + "_coordinates.txt";
    ofstream coord_file(coord_filename.c_str());
    coord_file << "# Node Coordinates (node_id x y)\n";
    coord_file << fixed << setprecision(4);  // 소수점 4자리까지 표시
    
    for (int i = 0; i < coordinates.size(); i++) {
        coord_file << i << " " << coordinates[i].first << " " << coordinates[i].second << "\n";
    }
    coord_file.close();
    
    cout << "Tour results saved in " << tour_filename << "." << endl;
    cout << "The coordinate data is saved in" << coord_filename << "." << endl;
} 