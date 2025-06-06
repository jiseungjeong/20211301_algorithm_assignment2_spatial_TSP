#ifndef HEAP_UTILS_H
#define HEAP_UTILS_H

#include <climits>
#include <cmath>

// Priority Queue Node 구조체 (double key용)
struct PQNode {
    int vertex;
    double key;
    
    PQNode() : vertex(-1), key(INFINITY) {}
    PQNode(int v, double k) : vertex(v), key(k) {}
};

// Priority Queue Node 구조체 (int key용)
struct PQNodeInt {
    int vertex;
    int key;
    
    PQNodeInt() : vertex(-1), key(INT_MAX) {}
    PQNodeInt(int v, int k) : vertex(v), key(k) {}
};

// Max-heap을 위한 Distance Node
struct DistNode {
    double dist;
    int id;
    
    DistNode() : dist(0), id(-1) {}
    DistNode(double d, int i) : dist(d), id(i) {}
};

// 힙 관련 함수들 (double key용)
int left_child(int i);
int right_child(int i);
void min_heapify(PQNode* heap, int heap_size, int i);
void max_heapify(DistNode* heap, int heap_size, int i);
void build_min_heap(PQNode* heap, int size);
void build_max_heap(DistNode* heap, int size);
PQNode extract_min(PQNode* heap, int& heap_size);
DistNode extract_max(DistNode* heap, int& heap_size);
void decrease_key(PQNode* heap, int heap_size, int vertex, double new_key);
void insert_max_heap(DistNode* heap, int& heap_size, int max_size, DistNode new_node);

// 힙 관련 함수들 (int key용)
void min_heapify_int(PQNodeInt* heap, int heap_size, int i);
void build_min_heap_int(PQNodeInt* heap, int size);
PQNodeInt extract_min_int(PQNodeInt* heap, int& heap_size);
void decrease_key_int(PQNodeInt* heap, int heap_size, int vertex, int new_key);

#endif // HEAP_UTILS_H 