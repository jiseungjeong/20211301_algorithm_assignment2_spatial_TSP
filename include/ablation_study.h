#ifndef ABLATION_STUDY_H
#define ABLATION_STUDY_H

#include <string>
#include <vector>
#include <fstream>

struct AblationStudyStats {
    std::string dataset_name;
    int nodes;
    
    // Phase 1 비교 (KD-tree vs Brute-force KNN)
    double kdtree_phase1_time_ms;
    double bruteforce_phase1_time_ms;
    double kdtree_candidate_edges;
    double bruteforce_candidate_edges;
    
    // Phase 4 비교 (2-opt 전후)
    double distance_before_2opt;
    double distance_after_2opt;
    double phase4_2opt_time_ms;
    double improvement_ratio_2opt;  // (before - after) / before
    
    // 전체 성능 비교
    double total_time_kdtree_ms;
    double total_time_bruteforce_ms;
    double final_distance_kdtree;
    double final_distance_bruteforce;
    
    // 시간 복잡도 분석
    double time_complexity_ratio;  // bruteforce_time / kdtree_time
    double quality_difference;     // |kdtree_distance - bruteforce_distance| / min(kdtree, bruteforce)
};

void saveAblationStats(const std::string& csv_file, const AblationStudyStats& stats) {
    std::ofstream file(csv_file, std::ios::app);
    if (file.is_open()) {
        file << stats.dataset_name << ","
             << stats.nodes << ","
             << stats.kdtree_phase1_time_ms << ","
             << stats.bruteforce_phase1_time_ms << ","
             << stats.kdtree_candidate_edges << ","
             << stats.bruteforce_candidate_edges << ","
             << stats.distance_before_2opt << ","
             << stats.distance_after_2opt << ","
             << stats.phase4_2opt_time_ms << ","
             << stats.improvement_ratio_2opt << ","
             << stats.total_time_kdtree_ms << ","
             << stats.total_time_bruteforce_ms << ","
             << stats.final_distance_kdtree << ","
             << stats.final_distance_bruteforce << ","
             << stats.time_complexity_ratio << ","
             << stats.quality_difference << std::endl;
        file.close();
    }
}

void initAblationStatsCSV(const std::string& csv_file) {
    std::ofstream file(csv_file);
    if (file.is_open()) {
        file << "Dataset,Nodes,KDTreePhase1TimeMs,BruteForcePhase1TimeMs,"
             << "KDTreeCandidateEdges,BruteForceCandidateEdges,"
             << "DistanceBefore2Opt,DistanceAfter2Opt,Phase4_2OptTimeMs,"
             << "ImprovementRatio2Opt,TotalTimeKDTreeMs,TotalTimeBruteForceMs,"
             << "FinalDistanceKDTree,FinalDistanceBruteForce,"
             << "TimeComplexityRatio,QualityDifference" << std::endl;
        file.close();
    }
}

#endif // ABLATION_STUDY_H 