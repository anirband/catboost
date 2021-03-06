LIBRARY()

NO_WERROR()



SRCS(
    kernel/pointwise_hist2.cu
    kernel/pointwise_hist2_binary.cu
    kernel/pointwise_hist2_half_byte.cu
    kernel/pointwise_hist2_one_byte_5bit.cu
    kernel/pointwise_hist2_one_byte_6bit.cu
    kernel/pointwise_hist2_one_byte_7bit.cu
    kernel/pointwise_hist2_one_byte_8bit.cu
    kernel/pointwise_hist1.cu
    kernel/pointwise_scores.cu
    kernel/linear_solver.cu
    kernel/pairwise_hist.cu
    kernel/pairwise_hist_binary.cu
    kernel/pairwise_hist_half_byte.cu
    kernel/pairwise_hist_one_byte_5bit.cu
    kernel/pairwise_hist_one_byte_6bit.cu
    kernel/pairwise_hist_one_byte_7bit.cu
    kernel/pairwise_hist_one_byte_8bit_atomics.cu
    kernel/split_pairwise.cu
    histograms_helper.cpp
    GLOBAL pointwise_kernels.cpp
    GLOBAL pairwise_kernels.cpp
    dynamic_boosting.cpp
    feature_parallel_pointwise_oblivious_tree.cpp
    oblivious_tree_structure_searcher.cpp
    leaves_estimation/oblivious_tree_leaves_estimator.cpp
    leaves_estimation/step_estimator.cpp
    leaves_estimation/leaves_estimation_helper.cpp
    boosting_progress_tracker.cpp
    boosting_metric_calcer.cpp
    tree_ctrs.cpp
    tree_ctrs_dataset.cpp
    serialization_helper.cpp
    pairwise_oblivious_trees/non_diagonal_leaves_estimator.cpp
    pairwise_oblivious_trees/pairwise_score_calcer_for_policy.cpp
    pairwise_oblivious_trees/pairwise_scores_calcer.cpp
    pairwise_oblivious_trees/blocked_histogram_helper.cpp
    pairwise_oblivious_trees/pairwise_oblivious_tree.cpp
    pairwise_oblivious_trees/pairwise_optimization_subsets.cpp
    pairwise_oblivious_trees/pairwise_structure_searcher.cpp

)

PEERDIR(
    catboost/cuda/models
    catboost/cuda/cuda_lib
    catboost/cuda/cuda_util
    catboost/cuda/data
    catboost/cuda/ctrs
    catboost/cuda/gpu_data
    catboost/cuda/targets
    catboost/libs/overfitting_detector
    catboost/libs/loggers
)

CUDA_NVCC_FLAGS(
    --expt-relaxed-constexpr
    -gencode arch=compute_30,code=compute_30
    -gencode arch=compute_35,code=sm_35
    -gencode arch=compute_50,code=compute_50
    -gencode arch=compute_52,code=sm_52
    -gencode arch=compute_60,code=compute_60
    -gencode arch=compute_61,code=compute_61
    -gencode arch=compute_61,code=sm_61
    -gencode arch=compute_70,code=sm_70
    -gencode arch=compute_70,code=compute_70
)


END()
