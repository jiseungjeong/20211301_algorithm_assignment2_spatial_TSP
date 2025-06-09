#ifndef BENCHMARK_UTILS_H
#define BENCHMARK_UTILS_H

#include <chrono>
#include <iostream>
#include <fstream>

class BenchmarkTimer {
private:
    std::chrono::high_resolution_clock::time_point start_time;
    std::chrono::high_resolution_clock::time_point end_time;
    
public:
    void start() {
        start_time = std::chrono::high_resolution_clock::now();
    }
    
    void stop() {
        end_time = std::chrono::high_resolution_clock::now();
    }
    
    double getMilliseconds() {
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
        return duration.count() / 1000.0; // Convert to milliseconds
    }
    
    double getSeconds() {
        return getMilliseconds() / 1000.0;
    }
};

void saveBenchmarkResult(const std::string& csv_file, const std::string& algorithm, 
                        const std::string& dataset, int nodes, double time_ms, int distance) {
    std::ofstream file(csv_file, std::ios::app);
    if (file.is_open()) {
        file << algorithm << "," << dataset << "," << nodes << "," 
             << time_ms << "," << distance << std::endl;
        file.close();
    }
}

#endif // BENCHMARK_UTILS_H 