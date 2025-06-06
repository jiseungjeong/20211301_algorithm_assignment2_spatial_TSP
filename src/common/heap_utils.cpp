#include "../../include/heap_utils.h"

int left_child(int i) {
    return 2 * i + 1;
}

int right_child(int i) {
    return 2 * i + 2;
}

void min_heapify(PQNode* heap, int heap_size, int i) {
    int left_i = left_child(i);
    int right_i = right_child(i);
    int smallest = i;
    
    if (left_i < heap_size && heap[left_i].key < heap[i].key) {
        smallest = left_i;
    }

    if (right_i < heap_size && heap[right_i].key < heap[smallest].key) {
        smallest = right_i;
    }
    
    if (smallest != i) {
        PQNode temp = heap[i];
        heap[i] = heap[smallest];
        heap[smallest] = temp;
        
        min_heapify(heap, heap_size, smallest);
    }
}

void max_heapify(DistNode* heap, int heap_size, int i) {
    int left_i = left_child(i);
    int right_i = right_child(i);
    int largest = i;
    
    if (left_i < heap_size && heap[left_i].dist > heap[i].dist) {
        largest = left_i;
    }

    if (right_i < heap_size && heap[right_i].dist > heap[largest].dist) {
        largest = right_i;
    }
    
    if (largest != i) {
        DistNode temp = heap[i];
        heap[i] = heap[largest];
        heap[largest] = temp;
        
        max_heapify(heap, heap_size, largest);
    }
}

void build_min_heap(PQNode* heap, int size) {
    for (int i = size / 2 - 1; i >= 0; i--) {
        min_heapify(heap, size, i);
    }
}

void build_max_heap(DistNode* heap, int size) {
    for (int i = size / 2 - 1; i >= 0; i--) {
        max_heapify(heap, size, i);
    }
}

PQNode extract_min(PQNode* heap, int& heap_size) {
    if (heap_size <= 0) {
        return PQNode(-1, INFINITY);
    }
    
    PQNode min_node = heap[0];
    heap[0] = heap[heap_size - 1];
    heap_size--;
    min_heapify(heap, heap_size, 0);
    
    return min_node;
}

DistNode extract_max(DistNode* heap, int& heap_size) {
    if (heap_size <= 0) {
        return DistNode(0, -1);
    }
    
    DistNode max_node = heap[0];
    heap[0] = heap[heap_size - 1];
    heap_size--;
    max_heapify(heap, heap_size, 0);
    
    return max_node;
}

void decrease_key(PQNode* heap, int heap_size, int vertex, double new_key) {
    int i = -1;
    for (int j = 0; j < heap_size; j++) {
        if (heap[j].vertex == vertex) {
            i = j;
            break;
        }
    }
    
    if (i == -1 || new_key >= heap[i].key) {
        return;
    }
    
    heap[i].key = new_key;
    
    while (i > 0 && heap[(i-1)/2].key > heap[i].key) {
        PQNode temp = heap[i];
        heap[i] = heap[(i-1)/2];
        heap[(i-1)/2] = temp;
        i = (i-1)/2;
    }
}

void insert_max_heap(DistNode* heap, int& heap_size, int max_size, DistNode new_node) {
    if (heap_size < max_size) {
        heap[heap_size] = new_node;
        heap_size++;
        
        // 위로 올라가며 정렬
        int i = heap_size - 1;
        while (i > 0 && heap[(i-1)/2].dist < heap[i].dist) {
            DistNode temp = heap[i];
            heap[i] = heap[(i-1)/2];
            heap[(i-1)/2] = temp;
            i = (i-1)/2;
        }
    } else if (new_node.dist < heap[0].dist) {
        heap[0] = new_node;
        max_heapify(heap, heap_size, 0);
    }
}

// Int key용 힙 함수들
void min_heapify_int(PQNodeInt* heap, int heap_size, int i) {
    int left_i = left_child(i);
    int right_i = right_child(i);
    int smallest = i;
    
    if (left_i < heap_size && heap[left_i].key < heap[i].key) {
        smallest = left_i;
    }

    if (right_i < heap_size && heap[right_i].key < heap[smallest].key) {
        smallest = right_i;
    }
    
    if (smallest != i) {
        PQNodeInt temp = heap[i];
        heap[i] = heap[smallest];
        heap[smallest] = temp;
        
        min_heapify_int(heap, heap_size, smallest);
    }
}

void build_min_heap_int(PQNodeInt* heap, int size) {
    for (int i = size / 2 - 1; i >= 0; i--) {
        min_heapify_int(heap, size, i);
    }
}

PQNodeInt extract_min_int(PQNodeInt* heap, int& heap_size) {
    if (heap_size <= 0) {
        return PQNodeInt(-1, INT_MAX);
    }
    
    PQNodeInt min_node = heap[0];
    heap[0] = heap[heap_size - 1];
    heap_size--;
    min_heapify_int(heap, heap_size, 0);
    
    return min_node;
}

void decrease_key_int(PQNodeInt* heap, int heap_size, int vertex, int new_key) {
    int i = -1;
    for (int j = 0; j < heap_size; j++) {
        if (heap[j].vertex == vertex) {
            i = j;
            break;
        }
    }
    
    if (i == -1 || new_key >= heap[i].key) {
        return;
    }
    
    heap[i].key = new_key;
    
    while (i > 0 && heap[(i-1)/2].key > heap[i].key) {
        PQNodeInt temp = heap[i];
        heap[i] = heap[(i-1)/2];
        heap[(i-1)/2] = temp;
        i = (i-1)/2;
    }
} 