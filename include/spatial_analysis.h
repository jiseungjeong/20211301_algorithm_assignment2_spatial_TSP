#ifndef SPATIAL_ANALYSIS_H
#define SPATIAL_ANALYSIS_H

#include <string>
#include <vector>
#include <fstream>

struct SpatialStats {
    std::string dataset_name;
    int nodes;
    double greedy_distance;
    double mst_distance;
    std::string winner;  // "Greedy" or "MST"
    double improvement_ratio;  // (worse - better) / worse
    
    // Ablation study results
    double phase1_time_ms;
    double phase2_time_ms; 
    double phase3_time_ms;
    double phase4_time_ms;
    double total_time_ms;
    
    // Phase-wise distances
    double greedy_only_distance;
    double mst_only_distance;
    double final_distance;
};

void saveSpatialStats(const std::string& csv_file, const SpatialStats& stats) {
    std::ofstream file(csv_file, std::ios::app);
    if (file.is_open()) {
        file << stats.dataset_name << ","
             << stats.nodes << ","
             << stats.greedy_distance << ","
             << stats.mst_distance << ","
             << stats.winner << ","
             << stats.improvement_ratio << ","
             << stats.phase1_time_ms << ","
             << stats.phase2_time_ms << ","
             << stats.phase3_time_ms << ","
             << stats.phase4_time_ms << ","
             << stats.total_time_ms << ","
             << stats.greedy_only_distance << ","
             << stats.mst_only_distance << ","
             << stats.final_distance << std::endl;
        file.close();
    }
}

void initSpatialStatsCSV(const std::string& csv_file) {
    std::ofstream file(csv_file);
    if (file.is_open()) {
        file << "Dataset,Nodes,GreedyDistance,MSTDistance,Winner,ImprovementRatio,"
             << "Phase1TimeMs,Phase2TimeMs,Phase3TimeMs,Phase4TimeMs,TotalTimeMs,"
             << "GreedyOnlyDistance,MSTOnlyDistance,FinalDistance" << std::endl;
        file.close();
    }
}

#endif // SPATIAL_ANALYSIS_H 