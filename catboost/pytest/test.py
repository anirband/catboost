import yatest.common
from yatest.common import network
import pytest
import os
import filecmp
import csv
import numpy as np
import time

import catboost
from catboost_pytest_lib import data_file, local_canonical_file, remove_time_from_json

CATBOOST_PATH = yatest.common.binary_path("catboost/app/catboost")
BOOSTING_TYPE = ['Ordered', 'Plain']


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_queryrmse(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_pool_with_QueryId(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd.query_id'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_rmse_on_qwise_pool(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'RMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_queryaverage(boosting_type):
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '--custom-metric', 'QueryAverage:top=2;hints=skip_train~false',
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
@pytest.mark.parametrize('top', [2, 100])
def test_queryaverage_with_query_weights(boosting_type, top):
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd.group_weight'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '--custom-metric', 'QueryAverage:top={};hints=skip_train~false'.format(top),
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('top_size', [2, 5, 10, -1])
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
@pytest.mark.parametrize('cd_file', ['train.cd', 'train.cd.subgroup_id'])
def test_pfound(top_size, boosting_type, cd_file):
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', cd_file),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '--custom-metric', 'PFound:top={};hints=skip_train~false'.format(top_size),
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_ndcg(boosting_type):
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '--custom-metric', 'NDCG:top={};hints=skip_train~false'.format(10),
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


def test_queryrmse_approx_on_full_history():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--approx-on-full-history',
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_pairlogit(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')

    def run_catboost(eval_path, learn_pairs):
        cmd = [
            CATBOOST_PATH,
            'fit',
            '--loss-function', 'PairLogit',
            '--eval-metric', 'PairAccuracy',
            '-f', data_file('querywise', 'train'),
            '-t', data_file('querywise', 'test'),
            '--column-description', data_file('querywise', 'train.cd'),
            '--learn-pairs', data_file('querywise', learn_pairs),
            '--test-pairs', data_file('querywise', 'test.pairs'),
            '--boosting-type', boosting_type,
            '--ctr', 'Borders,Counter',
            '--l2-leaf-reg', '0',
            '-i', '20',
            '-T', '4',
            '-r', '0',
            '-m', output_model_path,
            '--eval-file', eval_path,
            '--learn-err-log', learn_error_path,
            '--test-err-log', test_error_path,
            '--use-best-model', 'false',
        ]
        yatest.common.execute(cmd)

    run_catboost(output_eval_path, 'train.pairs')

    return [local_canonical_file(learn_error_path),
            local_canonical_file(test_error_path),
            local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_pairlogit_no_target(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'PairLogit',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd.no_target'),
        '--learn-pairs', data_file('querywise', 'train.pairs'),
        '--test-pairs', data_file('querywise', 'test.pairs'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_pairlogit_approx_on_full_history():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'PairLogit',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--learn-pairs', data_file('querywise', 'train.pairs'),
        '--test-pairs', data_file('querywise', 'test.pairs'),
        '--approx-on-full-history',
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('bagging_temperature', ['0', '1'])
def test_pairlogit_pairwise(bagging_temperature):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'PairLogitPairwise',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--learn-pairs', data_file('querywise', 'train.pairs'),
        '--test-pairs', data_file('querywise', 'test.pairs'),
        '--boosting-type', 'Plain',
        '--bagging-temperature', bagging_temperature,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_yetirank(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'YetiRank',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_yetirank_with_params(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'YetiRank:permutations=5;decay=0.9',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('bagging_temperature', ['0', '1'])
def test_yetirank_pairwise(bagging_temperature):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'YetiRankPairwise',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', 'Plain',
        '--bagging-temperature', bagging_temperature,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


NAN_MODE = ['Min', 'Max']


@pytest.mark.parametrize('nan_mode', NAN_MODE)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_nan_mode(nan_mode, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '-f', data_file('adult_nan', 'train_small'),
        '-t', data_file('adult_nan', 'test_small'),
        '--column-description', data_file('adult_nan', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--nan-mode', nan_mode,
    )
    yatest.common.execute(cmd)
    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult_nan', 'test_small'),
        '--column-description', data_file('adult_nan', 'train.cd'),
        '-m', output_model_path,
        '--output-path', formula_predict_path,
        '--prediction-type', 'RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)
    assert (compare_evals(output_eval_path, formula_predict_path))
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_nan_mode_forbidden(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--nan-mode', 'Forbidden',
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_overfit_detector_iter(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '2000',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '0.5',
        '--rsm', '1',
        '--od-type', 'Iter',
        '--od-wait', '1',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_overfit_detector_inc_to_dec(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '2000',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '0.5',
        '--rsm', '1',
        '--od-pval', '0.5',
        '--od-type', 'IncToDec',
        '--od-wait', '1',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_shrink_model(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '100',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '1',
        '--od-pval', '0.99',
        '--rsm', '1',
        '--use-best-model', 'true'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


LOSS_FUNCTIONS = ['RMSE', 'Logloss', 'MAE', 'CrossEntropy', 'Quantile', 'LogLinQuantile', 'Poisson', 'MAPE', 'MultiClass', 'MultiClassOneVsAll']


LEAF_ESTIMATION_METHOD = ['Gradient', 'Newton']


@pytest.mark.parametrize('leaf_estimation_method', LEAF_ESTIMATION_METHOD)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_multi_leaf_estimation_method(leaf_estimation_method, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'MultiClass',
        '-f', data_file('cloudness_small', 'train_small'),
        '-t', data_file('cloudness_small', 'test_small'),
        '--column-description', data_file('cloudness_small', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--leaf-estimation-method', leaf_estimation_method,
        '--leaf-estimation-iterations', '2',
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)
    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('cloudness_small', 'test_small'),
        '--column-description', data_file('cloudness_small', 'train.cd'),
        '-m', output_model_path,
        '--output-path', formula_predict_path,
        '--prediction-type', 'RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)
    assert(compare_evals(output_eval_path, formula_predict_path))
    return [local_canonical_file(output_eval_path)]


LOSS_FUNCTIONS_SHORT = ['Logloss', 'MultiClass']


@pytest.mark.parametrize('loss_function', LOSS_FUNCTIONS_SHORT)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_doc_id(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', loss_function,
        '-f', data_file('adult_doc_id', 'train'),
        '-t', data_file('adult_doc_id', 'test'),
        '--column-description', data_file('adult_doc_id', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


POOLS = ['amazon', 'adult']


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_apply_missing_vals(boosting_type):
    model_path = yatest.common.test_output_path('adult_model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('test_adult_missing_val.tsv'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', model_path,
        '--output-path', output_eval_path
    )
    yatest.common.execute(calc_cmd)

    return local_canonical_file(output_eval_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_crossentropy(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'CrossEntropy',
        '-f', data_file('adult_crossentropy', 'train_proba'),
        '-t', data_file('adult_crossentropy', 'test_proba'),
        '--column-description', data_file('adult_crossentropy', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_permutation_block(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--fold-permutation-block', '239',
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_ignored_features(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-I', '0:1:3:5-7',
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


def test_ignored_features_not_read():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    input_cd_path = data_file('adult', 'train.cd')
    cd_path = yatest.common.test_output_path('train.cd')

    with open(input_cd_path, "rt") as f:
        cd_lines = f.readlines()
    with open(cd_path, "wt") as f:
        for cd_line in cd_lines:
            # Corrupt some features by making them 'Num'
            if cd_line.split() == ('5', 'Categ'):  # column 5 --> feature 4
                cd_line = cd_line.replace('Categ', 'Num')
            if cd_line.split() == ('7', 'Categ'):  # column 7 --> feature 6
                cd_line = cd_line.replace('Categ', 'Num')
            f.write(cd_line)

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', cd_path,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-I', '4:6',  # Ignore the corrupted features
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)
    # Not needed: return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_baseline(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('train_adult_baseline.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('train_adult_baseline.cd'),
        '-m', output_model_path,
        '--output-path', formula_predict_path,
        '--prediction-type', 'RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)
    assert(compare_evals(output_eval_path, formula_predict_path))
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_weights(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('adult_weight', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_weights_no_bootstrap(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('adult_weight', 'train.cd'),
        '--boosting-type', boosting_type,
        '--bootstrap-type', 'No',
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_weights_gradient(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('adult_weight', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--leaf-estimation-method', 'Gradient'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_logloss_with_not_binarized_target(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_not_binarized', 'train_small'),
        '-t', data_file('adult_not_binarized', 'test_small'),
        '--column-description', data_file('adult_not_binarized', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('loss_function', LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_all_targets(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', output_model_path,
        '--output-path', formula_predict_path,
        '--prediction-type', 'RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)
    if loss_function == 'MAPE':
        # TODO(kirillovs): uncomment this after resolving MAPE problems
        # assert(compare_evals(output_eval_path, formula_predict_path))
        return [local_canonical_file(output_eval_path), local_canonical_file(formula_predict_path)]
    else:
        assert(compare_evals(output_eval_path, formula_predict_path))
        return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_cv(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-X', '2/10',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_inverted_cv(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-Y', '2/10',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_cv_for_query(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-X', '2/7',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_cv_for_pairs(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'PairLogit',
        '-f', data_file('querywise', 'train'),
        '--column-description', data_file('querywise', 'train.cd'),
        '--learn-pairs', data_file('querywise', 'train.pairs'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '-X', '2/7',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_empty_eval(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_time(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--has-time',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_gradient(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--leaf-estimation-method', 'Gradient',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_newton(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--leaf-estimation-method', 'Newton',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_newton_on_pool_with_weights(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('adult_weight', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--leaf-estimation-method', 'Newton',
        '--leaf-estimation-iterations', '7',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_custom_priors(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--ctr', 'Borders:Prior=-2:Prior=0:Prior=8:Prior=1:Prior=-1:Prior=3,'
                 'Counter:Prior=0',
        '--per-feature-ctr', '4:Borders:Prior=0.444,Counter:Prior=0.444;'
                             '6:Borders:Prior=0.666,Counter:Prior=0.666;'
                             '8:Borders:Prior=-0.888:Prior=0.888,Counter:Prior=-0.888:Prior=0.888',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_ctr_buckets(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'MultiClass',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--ctr', 'Buckets'
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_fold_len_multiplier(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'MultiClass',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--fold-len-multiplier', '1.5'
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


FSTR_TYPES = ['FeatureImportance', 'InternalFeatureImportance', 'Doc', 'InternalInteraction', 'Interaction', 'ShapValues']


@pytest.mark.parametrize('fstr_type', FSTR_TYPES)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_fstr(fstr_type, boosting_type):
    model_path = yatest.common.test_output_path('adult_model.bin')
    output_fstr_path = yatest.common.test_output_path('fstr.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '--one-hot-max-size', '10',
        '-m', model_path
    )

    if fstr_type == 'ShapValues':
        cmd = cmd + ('--max-ctr-complexity', '1')

    yatest.common.execute(cmd)

    fstr_cmd = (
        CATBOOST_PATH,
        'fstr',
        '--input-path', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', model_path,
        '-o', output_fstr_path,
        '--fstr-type', fstr_type
    )
    yatest.common.execute(fstr_cmd)

    return local_canonical_file(output_fstr_path)


def test_reproducibility():
    def run_catboost(threads, model_path, eval_path):
        cmd = [
            CATBOOST_PATH,
            'fit',
            '--use-best-model', 'false',
            '--loss-function', 'Logloss',
            '-f', data_file('adult', 'train_small'),
            '-t', data_file('adult', 'test_small'),
            '--column-description', data_file('adult', 'train.cd'),
            '-i', '25',
            '-T', str(threads),
            '-r', '0',
            '-m', model_path,
            '--eval-file', eval_path,
        ]
        yatest.common.execute(cmd)
    model_1 = yatest.common.test_output_path('model_1.bin')
    eval_1 = yatest.common.test_output_path('test_1.eval')
    run_catboost(1, model_1, eval_1)
    model_4 = yatest.common.test_output_path('model_4.bin')
    eval_4 = yatest.common.test_output_path('test_4.eval')
    run_catboost(4, model_4, eval_4)
    assert filecmp.cmp(eval_1, eval_4)


BORDER_TYPES = ['Median', 'GreedyLogSum', 'UniformAndQuantiles', 'MinEntropy', 'MaxLogSum', 'Uniform']


@pytest.mark.parametrize('border_type', BORDER_TYPES)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_feature_border_types(border_type, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--feature-border-type', border_type,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('depth', [4, 8])
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_deep_tree_classification(depth, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '--depth', str(depth),
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_regularization(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--leaf-estimation-method', 'Newton',
        '--eval-file', output_eval_path,
        '--l2-leaf-reg', '5'
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


REG_LOSS_FUNCTIONS = ['RMSE', 'MAE', 'Quantile', 'LogLinQuantile', 'Poisson', 'MAPE']


@pytest.mark.parametrize('loss_function', REG_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_reg_targets(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('adult_crossentropy', 'train_proba'),
        '-t', data_file('adult_crossentropy', 'test_proba'),
        '--column-description', data_file('adult_crossentropy', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


MULTI_LOSS_FUNCTIONS = ['MultiClass', 'MultiClassOneVsAll']


@pytest.mark.parametrize('loss_function', MULTI_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_multi_targets(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('cloudness_small', 'train_small'),
        '-t', data_file('cloudness_small', 'test_small'),
        '--column-description', data_file('cloudness_small', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path
    )
    yatest.common.execute(cmd)

    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('cloudness_small', 'test_small'),
        '--column-description', data_file('cloudness_small', 'train.cd'),
        '-m', output_model_path,
        '--output-path', formula_predict_path,
        '--prediction-type', 'RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)
    assert(compare_evals(output_eval_path, formula_predict_path))
    return [local_canonical_file(output_eval_path)]


BORDER_TYPES = ['MinEntropy', 'Median', 'UniformAndQuantiles', 'MaxLogSum', 'GreedyLogSum', 'Uniform']


@pytest.mark.parametrize('border_type', BORDER_TYPES)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_target_border(border_type, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file('adult_crossentropy', 'train_proba'),
        '-t', data_file('adult_crossentropy', 'test_proba'),
        '--column-description', data_file('adult_crossentropy', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '3',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--ctr', 'Borders:TargetBorderCount=3:TargetBorderType=' + border_type
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


COUNTER_METHODS = ['Full', 'SkipTest']


@pytest.mark.parametrize('counter_calc_method', COUNTER_METHODS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_counter_calc(counter_calc_method, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file('adult_crossentropy', 'train_proba'),
        '-t', data_file('adult_crossentropy', 'test_proba'),
        '--column-description', data_file('adult_crossentropy', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '60',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--counter-calc-method', counter_calc_method
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


CTR_TYPES = ['Borders', 'Buckets', 'BinarizedTargetMeanValue:TargetBorderCount=10', 'Borders,BinarizedTargetMeanValue:TargetBorderCount=10', 'Buckets,Borders']


@pytest.mark.parametrize('ctr_type', CTR_TYPES)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_ctr_type(ctr_type, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file('adult_crossentropy', 'train_proba'),
        '-t', data_file('adult_crossentropy', 'test_proba'),
        '--column-description', data_file('adult_crossentropy', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '3',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--ctr', ctr_type
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_custom_overfitting_detector_metric(boosting_type):
    model_path = yatest.common.test_output_path('adult_model.bin')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '--eval-metric', 'AUC:hints=skip_train~false',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path),
            local_canonical_file(test_error_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_custom_loss_for_classification(boosting_type):
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '--custom-metric',
        'AUC:hints=skip_train~false,CrossEntropy,Accuracy,Precision,Recall,F1,TotalF1,MCC,BalancedAccuracy,BalancedErrorRate,Kappa,WKappa,BrierScore,ZeroOneLoss,HammingLoss,HingeLoss',
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_custom_loss_for_multiclassification(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'MultiClass',
        '-f', data_file('cloudness_small', 'train_small'),
        '-t', data_file('cloudness_small', 'test_small'),
        '--column-description', data_file('cloudness_small', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--custom-metric',
        'AUC:hints=skip_train~false,Accuracy,Precision,Recall,F1,TotalF1,MultiClassOneVsAll,MCC,Kappa,WKappa,ZeroOneLoss,HammingLoss,HingeLoss',
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_calc_prediction_type(boosting_type):
    model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
    )
    yatest.common.execute(cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', model_path,
        '--output-path', output_eval_path,
        '--prediction-type', 'Probability'
    )
    yatest.common.execute(calc_cmd)

    return local_canonical_file(output_eval_path)


def compare_evals(fit_eval, calc_eval):
    csv_fit = csv.reader(open(fit_eval, "r"), dialect='excel-tab')
    csv_calc = csv.reader(open(calc_eval, "r"), dialect='excel-tab')
    while True:
        try:
            line_fit = next(csv_fit)
            line_calc = next(csv_calc)
            if line_fit[:-1] != line_calc:
                return False
        except StopIteration:
            break
    return True


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_calc_no_target(boosting_type):
    model_path = yatest.common.test_output_path('adult_model.bin')
    fit_output_eval_path = yatest.common.test_output_path('fit_test.eval')
    calc_output_eval_path = yatest.common.test_output_path('calc_test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
        '--counter-calc-method', 'SkipTest',
        '--eval-file', fit_output_eval_path
    )
    yatest.common.execute(cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('train_notarget.cd'),
        '-m', model_path,
        '--output-path', calc_output_eval_path
    )
    yatest.common.execute(calc_cmd)

    assert(compare_evals(fit_output_eval_path, calc_output_eval_path))


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_classification_progress_restore(boosting_type):
    def run_catboost(iters, model_path, eval_path, additional_params=None):
        import random
        import shutil
        import string
        letters = string.ascii_lowercase
        train_random_name = ''.join(random.choice(letters) for i in xrange(8))
        shutil.copy(data_file('adult', 'train_small'), train_random_name)
        cmd = [
            CATBOOST_PATH,
            'fit',
            '--loss-function', 'Logloss',
            '--learning-rate', '0.5',
            '-f', train_random_name,
            '-t', data_file('adult', 'test_small'),
            '--column-description', data_file('adult', 'train.cd'),
            '--boosting-type', boosting_type,
            '-i', str(iters),
            '-T', '4',
            '-r', '0',
            '-m', model_path,
            '--eval-file', eval_path,
        ]
        if additional_params:
            cmd += additional_params
        yatest.common.execute(cmd)
    canon_model_path = yatest.common.test_output_path('canon_model.bin')
    canon_eval_path = yatest.common.test_output_path('canon_test.eval')
    run_catboost(30, canon_model_path, canon_eval_path)
    model_path = yatest.common.test_output_path('model.bin')
    eval_path = yatest.common.test_output_path('test.eval')
    progress_path = yatest.common.test_output_path('test.cbp')
    run_catboost(15, model_path, eval_path, additional_params=['--snapshot-file', progress_path])
    run_catboost(30, model_path, eval_path, additional_params=['--snapshot-file', progress_path])
    assert filecmp.cmp(canon_eval_path, eval_path)
    # TODO(kirillovs): make this active when progress_file parameter will be deleted from json params
    # assert filecmp.cmp(canon_model_path, model_path)


CLASSIFICATION_LOSSES = ['Logloss', 'CrossEntropy', 'MultiClass', 'MultiClassOneVsAll']
PREDICTION_TYPES = ['RawFormulaVal', 'Class', 'Probability']


@pytest.mark.parametrize('loss_function', CLASSIFICATION_LOSSES)
@pytest.mark.parametrize('prediction_type', PREDICTION_TYPES)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_prediction_type(prediction_type, loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--prediction-type', prediction_type
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_const_feature(boosting_type):
    pool = 'no_split'
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file(pool, 'train_full3'),
        '-t', data_file(pool, 'test3'),
        '--column-description', data_file(pool, 'train_full3.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


QUANTILE_LOSS_FUNCTIONS = ['Quantile', 'LogLinQuantile']


@pytest.mark.parametrize('loss_function', QUANTILE_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_quantile_targets(loss_function, boosting_type):
    pool = 'no_split'
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function + ':alpha=0.9',
        '-f', data_file(pool, 'train_full3'),
        '-t', data_file(pool, 'test3'),
        '--column-description', data_file(pool, 'train_full3.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


CUSTOM_LOSS_FUNCTIONS = ['RMSE,MAE', 'Quantile:alpha=0.9', 'MSLE,MedianAbsoluteError']


@pytest.mark.parametrize('custom_loss_function', CUSTOM_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_custom_loss(custom_loss_function, boosting_type):
    pool = 'no_split'
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file(pool, 'train_full3'),
        '-t', data_file(pool, 'test3'),
        '--column-description', data_file(pool, 'train_full3.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--custom-metric', custom_loss_function,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path), local_canonical_file(test_error_path)]


@pytest.mark.parametrize('loss_function', LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_meta(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    meta_path = 'meta.tsv'
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--name', 'test experiment',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(meta_path)]


def test_train_dir():
    pool = 'no_split'
    output_model_path = 'model.bin'
    output_eval_path = 'test.eval'
    train_dir_path = 'trainDir'
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file(pool, 'train_full3'),
        '-t', data_file(pool, 'test3'),
        '--column-description', data_file(pool, 'train_full3.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--train-dir', train_dir_path,
        '--fstr-file', 'fstr.tsv',
        '--fstr-internal-file', 'ifstr.tsv'
    )
    yatest.common.execute(cmd)
    outputs = ['time_left.tsv', 'learn_error.tsv', 'test_error.tsv', 'meta.tsv', output_model_path, output_eval_path, 'fstr.tsv', 'ifstr.tsv']
    for output in outputs:
        assert os.path.isfile(train_dir_path + '/' + output)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_feature_id_fstr(boosting_type):
    model_path = yatest.common.test_output_path('adult_model.bin')
    output_fstr_path = yatest.common.test_output_path('fstr.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
    )
    yatest.common.execute(cmd)

    fstr_cmd = (
        CATBOOST_PATH,
        'fstr',
        '--input-path', data_file('adult', 'train_small'),
        '--column-description', data_file('adult_with_id.cd'),
        '-m', model_path,
        '-o', output_fstr_path,
    )
    yatest.common.execute(fstr_cmd)

    return local_canonical_file(output_fstr_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_class_names_logloss(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--class-names', '1,0'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('loss_function', MULTI_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_class_names_multiclass(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('precipitation_small', 'train_small'),
        '-t', data_file('precipitation_small', 'test_small'),
        '--column-description', data_file('precipitation_small', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--class-names', '0.,0.5,1.,0.25,0.75'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_class_weight_logloss(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--class-weights', '0.5,2'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('loss_function', MULTI_LOSS_FUNCTIONS)
@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_class_weight_multiclass(loss_function, boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', loss_function,
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--class-weights', '0.5,2'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_params_from_file(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '6',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--params-file', data_file('params.json')
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_lost_class(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'MultiClass',
        '-f', data_file('cloudness_lost_class', 'train_small'),
        '-t', data_file('cloudness_lost_class', 'test_small'),
        '--column-description', data_file('cloudness_lost_class', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--classes-count', '3'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_class_weight_with_lost_class(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'MultiClass',
        '-f', data_file('cloudness_lost_class', 'train_small'),
        '-t', data_file('cloudness_lost_class', 'test_small'),
        '--column-description', data_file('cloudness_lost_class', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--classes-count', '3',
        '--class-weights', '0.5,2,2'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_one_hot(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    calc_eval_path = yatest.common.test_output_path('calc.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '100',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '0.1',
        '--one-hot-max-size', '10'
    )
    yatest.common.execute(cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', output_model_path,
        '--output-path', calc_eval_path
    )
    yatest.common.execute(calc_cmd)

    assert(compare_evals(output_eval_path, calc_eval_path))
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_random_strength(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '100',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '0.1',
        '--random-strength', '100'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_only_categorical_features(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult_all_categorical.cd'),
        '--boosting-type', boosting_type,
        '-i', '100',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-x', '1',
        '-n', '8',
        '-w', '0.1',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_weight_sampling_per_tree(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--sampling-frequency', 'PerTree',
    )
    yatest.common.execute(cmd)
    return local_canonical_file(output_eval_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_allow_writing_files_and_used_ram_limit(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--allow-writing-files', 'false',
        '--used-ram-limit', '1024',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '100',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_subsample_per_tree(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--sampling-frequency', 'PerTree',
        '--bootstrap-type', 'Bernoulli',
        '--subsample', '0.5',
    )
    yatest.common.execute(cmd)
    return local_canonical_file(output_eval_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_subsample_per_tree_level(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--bootstrap-type', 'Bernoulli',
        '--subsample', '0.5',
    )
    yatest.common.execute(cmd)
    return local_canonical_file(output_eval_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_bagging_per_tree_level(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--bagging-temperature', '0.5',
    )
    yatest.common.execute(cmd)
    return local_canonical_file(output_eval_path)


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_plain(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--boosting-type', 'Plain',
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_bootstrap(boosting_type):
    bootstrap_option = {
        'no': ('--bootstrap-type', 'No',),
        'bayes': ('--bootstrap-type', 'Bayesian', '--bagging-temperature', '0.0',),
        'bernoulli': ('--bootstrap-type', 'Bernoulli', '--subsample', '1.0',)
    }
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
    )
    for bootstrap in bootstrap_option:
        model_path = yatest.common.test_output_path('model_' + bootstrap + '.bin')
        eval_path = yatest.common.test_output_path('test_' + bootstrap + '.eval')
        yatest.common.execute(cmd + ('-m', model_path, '--eval-file', eval_path,) + bootstrap_option[bootstrap])

    ref_eval_path = yatest.common.test_output_path('test_no.eval')
    assert(filecmp.cmp(ref_eval_path, yatest.common.test_output_path('test_bayes.eval')))
    assert(filecmp.cmp(ref_eval_path, yatest.common.test_output_path('test_bernoulli.eval')))

    return [local_canonical_file(ref_eval_path)]


def test_json_logging():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    json_path = yatest.common.test_output_path('catboost_training.json')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--json-log', json_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(remove_time_from_json(json_path))]


def test_json_logging_metric_period():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    json_path = yatest.common.test_output_path('catboost_training.json')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--json-log', json_path,
        '--metric-period', '2',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(remove_time_from_json(json_path))]


def test_output_columns_format():
    model_path = yatest.common.test_output_path('adult_model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        # Intentionally skipped: -t ...
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
        '--output-columns', 'DocId,RawFormulaVal,#2,Label',
        '--eval-file', output_eval_path
    )
    yatest.common.execute(cmd)

    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', model_path,
        '--output-path', formula_predict_path,
        '--output-columns', 'DocId,RawFormulaVal'
    )
    yatest.common.execute(calc_cmd)

    return local_canonical_file(output_eval_path, formula_predict_path)


def test_eval_period():
    model_path = yatest.common.test_output_path('adult_model.bin')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '-f', data_file('adult', 'train_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', model_path,
    )
    yatest.common.execute(cmd)

    formula_predict_path = yatest.common.test_output_path('predict_test.eval')

    calc_cmd = (
        CATBOOST_PATH,
        'calc',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', model_path,
        '--output-path', formula_predict_path,
        '--eval-period', '2'
    )
    yatest.common.execute(calc_cmd)

    return local_canonical_file(formula_predict_path)


def test_weights_output():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('adult_weight', 'train.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--output-columns', 'DocId,RawFormulaVal,Weight,Label',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_baseline_output():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult_weight', 'train_weight'),
        '-t', data_file('adult_weight', 'test_weight'),
        '--column-description', data_file('train_adult_baseline.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--output-columns', 'DocId,RawFormulaVal,Baseline,Label',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_query_output():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--output-columns', 'DocId,Label,RawFormulaVal,GroupId',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_without_cat_features(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'RMSE',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-w', '0.1',
        '--one-hot-max-size', '102',
        '--bootstrap-type', 'No',
        '--random-strength', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def run_dist_train(cd_file):
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('higgs', 'train_small'),
        '-t', data_file('higgs', 'test_small'),
        '--column-description', data_file('higgs', cd_file),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '--random-strength', '0',
        '--has-time',
        '--bootstrap-type', 'No',
        '--boosting-type', 'Plain',
    )

    eval_0_path = yatest.common.test_output_path('test_0.eval')
    yatest.common.execute(cmd + ('--eval-file', eval_0_path,))

    hosts_path = yatest.common.test_output_path('hosts.txt')
    with network.PortManager() as pm:
        port0 = pm.get_port()
        port1 = pm.get_port()
        with open(hosts_path, 'w') as hosts:
            hosts.write('localhost:' + str(port0) + '\n')
            hosts.write('localhost:' + str(port1) + '\n')
        hosts.close()

        worker_0 = yatest.common.execute(cmd + ('--node-type', 'Worker', '--node-port', str(port0), ), wait=False)
        worker_1 = yatest.common.execute(cmd + ('--node-type', 'Worker', '--node-port', str(port1), ), wait=False)
        while worker_0.std_out == '' or worker_1.std_out == '':
            time.sleep(1)

        eval_1_path = yatest.common.test_output_path('test_1.eval')
        yatest.common.execute(
            cmd + ('--node-type', 'Master', '--file-with-hosts', hosts_path, '--eval-file', eval_1_path,)
        )

    assert(filecmp.cmp(eval_0_path, eval_1_path))
    return eval_0_path


def test_dist_train():
    return [local_canonical_file(run_dist_train('train.cd'))]


def test_dist_train_with_weights():
    return [local_canonical_file(run_dist_train('train_weight.cd'))]


def test_dist_train_with_baseline():
    return [local_canonical_file(run_dist_train('train_baseline.cd'))]


def test_no_target():
    train_path = yatest.common.test_output_path('train')
    cd_path = yatest.common.test_output_path('train.cd')
    pairs_path = yatest.common.test_output_path('pairs')

    np.savetxt(train_path, [[0], [1], [2], [3], [4]], delimiter='\t', fmt='%.4f')
    np.savetxt(cd_path, [('0', 'Num')], delimiter='\t', fmt='%s')
    np.savetxt(pairs_path, [[0, 1], [0, 2], [0, 3], [2, 4]], delimiter='\t', fmt='%i')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '-f', train_path,
        '--cd', cd_path,
        '--learn-pairs', pairs_path
    )
    with pytest.raises(yatest.common.ExecutionError):
        yatest.common.execute(cmd)


def test_negative_weights():
    train_path = yatest.common.test_output_path('train')
    cd_path = yatest.common.test_output_path('train.cd')

    open(cd_path, 'wt').write('0\tNum\n1\tWeight\n2\tTarget\n')
    np.savetxt(train_path, [
        [0, 1, 2],
        [1, -1, 1]], delimiter='\t', fmt='%.4f')
    cmd = (CATBOOST_PATH, 'fit',
           '-f', train_path,
           '--cd', cd_path,
           )
    with pytest.raises(yatest.common.ExecutionError):
        yatest.common.execute(cmd)


@pytest.mark.parametrize('metric', ['Logloss', 'F1', 'Accuracy', 'PFound', 'TotalF1', 'MCC'])
def test_eval_metrics(metric):
    train, test, cd, loss_function = data_file('adult', 'train_small'), data_file('adult', 'test_small'), data_file('adult', 'train.cd'), 'Logloss'
    if metric == 'PFound':
        train, test, cd, loss_function = data_file('querywise', 'train'), data_file('querywise', 'test'), data_file('querywise', 'train.cd'), 'QueryRMSE'

    output_model_path = yatest.common.test_output_path('model.bin')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    eval_path = yatest.common.test_output_path('output.tsv')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', loss_function,
        '--eval-metric', metric,
        '-f', train,
        '-t', test,
        '--column-description', cd,
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false'
    )
    yatest.common.execute(cmd)

    cmd = (
        CATBOOST_PATH,
        'eval-metrics',
        '--metrics', metric,
        '--input-path', test,
        '--column-description', cd,
        '-m', output_model_path,
        '-o', eval_path,
        '--block-size', '100',
        '--save-stats'
    )
    yatest.common.execute(cmd)

    first_metrics = np.round(np.loadtxt(test_error_path, skiprows=1)[:, 1], 8)
    second_metrics = np.round(np.loadtxt(eval_path, skiprows=1)[:, 1], 8)
    assert np.all(first_metrics == second_metrics)

    return [local_canonical_file('partial_stats.tsv')]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_ctr_leaf_count_limit(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '--ctr-leaf-count-limit', '10',
        '-i', '30',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_eval_non_additive_metric():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '10',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
    )
    yatest.common.execute(cmd)

    cmd = (
        CATBOOST_PATH,
        'eval-metrics',
        '--metrics', 'AUC:hints=skip_train~false',
        '--input-path', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', output_model_path,
        '-o', output_eval_path,
        '--block-size', '10'
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', ['Plain', 'Ordered'])
@pytest.mark.parametrize('max_ctr_complexity', [1, 2])
def test_eval_eq_calc(boosting_type, max_ctr_complexity):
    one_hot_max_size = 2
    cd_path = yatest.common.test_output_path('cd.txt')
    train_path = yatest.common.test_output_path('train.txt')
    test_path = yatest.common.test_output_path('test.txt')
    model_path = yatest.common.test_output_path('model.bin')
    test_eval_path = yatest.common.test_output_path('test.eval')
    calc_eval_path = yatest.common.test_output_path('calc.eval')

    np.savetxt(cd_path, [['0', 'Target'],
                         ['1', 'Categ'],
                         ['2', 'Categ']
                         ], fmt='%s', delimiter='\t')
    np.savetxt(train_path, [['1', 'A', 'X'],
                            ['1', 'B', 'Y'],
                            ['1', 'C', 'Y'],
                            ['0', 'A', 'Z'],
                            ['0', 'B', 'Z'],
                            ], fmt='%s', delimiter='\t')
    np.savetxt(test_path, [['1', 'A', 'Y'],
                           ['1', 'D', 'U'],
                           ['1', 'D', 'U']
                           ], fmt='%s', delimiter='\t')
    cmd_fit = (CATBOOST_PATH, 'fit',
               '--loss-function', 'Logloss',
               '--boosting-type', boosting_type,
               '--cd', cd_path,
               '-f', train_path,
               '-t', test_path,
               '-m', model_path,
               '--eval-file', test_eval_path,
               '-i', '5',
               '-r', '0',
               '-T', '1',
               '--max-ctr-complexity', str(max_ctr_complexity),
               '--one-hot-max-size', str(one_hot_max_size),
               )
    cmd_calc = (CATBOOST_PATH, 'calc',
                '--cd', cd_path,
                '--input-path', test_path,
                '-m', model_path,
                '-T', '1',
                '--output-path', calc_eval_path,
                )
    yatest.common.execute(cmd_fit)
    yatest.common.execute(cmd_calc)
    assert(compare_evals(test_eval_path, calc_eval_path))


@pytest.mark.parametrize('loss_function', ['RMSE', 'Logloss', 'Poisson'])
@pytest.mark.parametrize('leaf_estimation_iteration', ['1', '2'])
def test_object_importances(loss_function, leaf_estimation_iteration):
    output_model_path = yatest.common.test_output_path('model.bin')
    object_importances_path = yatest.common.test_output_path('object_importances.tsv')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', loss_function,
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '10',
        '--leaf-estimation-method', 'Gradient',
        '--leaf-estimation-iterations', leaf_estimation_iteration,
        '--boosting-type', 'Plain',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--use-best-model', 'false'
    )
    yatest.common.execute(cmd)

    cmd = (
        CATBOOST_PATH,
        'ostr',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-m', output_model_path,
        '-o', object_importances_path,
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(object_importances_path)]


# Create `num_tests` test files from `test_input_path`.
def split_test_to(num_tests, test_input_path):
    test_input_lines = open(test_input_path).readlines()
    test_paths = [yatest.common.test_output_path('test{}'.format(i)) for i in range(num_tests)]
    for testno in range(num_tests):
        test_path = test_paths[testno]
        test_lines = test_input_lines[testno::num_tests]
        open(test_path, 'wt').write(''.join(test_lines))
    return test_paths


# Create a few shuffles from list of test files, for use with `-t` option.
def create_test_shuffles(test_paths):
    num_tests = len(test_paths)
    num_shuffles = num_tests  # if num_tests < 3 else num_tests * (num_tests - 1)
    test_shuffles = set()
    while len(test_shuffles) < num_shuffles:
        test_shuffles.add(tuple(np.random.permutation(test_paths)))
    return [','.join(shuffle) for shuffle in test_shuffles]


def fit_calc_cksum(fit_stem, calc_stem, test_shuffles):
    import hashlib
    last_cksum = None
    for i, shuffle in enumerate(test_shuffles):
        model_path = yatest.common.test_output_path('model{}.bin'.format(i))
        eval_path = yatest.common.test_output_path('eval{}.txt'.format(i))
        yatest.common.execute(fit_stem + (
            '-t', shuffle,
            '-m', model_path,
        ))
        yatest.common.execute(calc_stem + (
            '-m', model_path,
            '--output-path', eval_path,
        ))
        cksum = hashlib.md5(open(eval_path).read()).hexdigest()
        if last_cksum is None:
            last_cksum = cksum
            continue
        assert(last_cksum == cksum)


@pytest.mark.parametrize('num_tests', [3, 4])
@pytest.mark.parametrize('boosting_type', ['Plain', 'Ordered'])
def test_multiple_eval_sets_order_independent(boosting_type, num_tests):
    train_path = data_file('adult', 'train_small')
    cd_path = data_file('adult', 'train.cd')
    test_input_path = data_file('adult', 'test_small')
    fit_stem = (CATBOOST_PATH, 'fit',
                '--loss-function', 'RMSE',
                '-f', train_path,
                '--cd', cd_path,
                '--boosting-type', boosting_type,
                '-i', '5',
                '-T', '4',
                '-r', '0',
                '--use-best-model', 'false',
                )
    calc_stem = (CATBOOST_PATH, 'calc',
                 '--cd', cd_path,
                 '--input-path', test_input_path,
                 '-T', '4',
                 )
    # We use a few shuffles of tests and check equivalence of resulting models
    test_shuffles = create_test_shuffles(split_test_to(num_tests, test_input_path))
    fit_calc_cksum(fit_stem, calc_stem, test_shuffles)


@pytest.mark.parametrize('num_tests', [3, 4])
@pytest.mark.parametrize('boosting_type', ['Plain', 'Ordered'])
def test_multiple_eval_sets_querywise_order_independent(boosting_type, num_tests):
    train_path = data_file('querywise', 'train')
    cd_path = data_file('querywise', 'train.cd.query_id')
    test_input_path = data_file('querywise', 'test')
    fit_stem = (CATBOOST_PATH, 'fit',
                '--loss-function', 'QueryRMSE',
                '-f', train_path,
                '--cd', cd_path,
                '--boosting-type', boosting_type,
                '-i', '5',
                '-T', '4',
                '-r', '0',
                '--use-best-model', 'false',
                )
    calc_stem = (CATBOOST_PATH, 'calc',
                 '--cd', cd_path,
                 '--input-path', test_input_path,
                 '-T', '4',
                 )
    # We use a few shuffles of tests and check equivalence of resulting models
    test_shuffles = create_test_shuffles(split_test_to(num_tests, test_input_path))
    fit_calc_cksum(fit_stem, calc_stem, test_shuffles)


def test_multiple_eval_sets_no_empty():
    train_path = data_file('adult', 'train_small')
    cd_path = data_file('adult', 'train.cd')
    test_input_path = data_file('adult', 'test_small')
    fit_stem = (CATBOOST_PATH, 'fit',
                '--loss-function', 'RMSE',
                '-f', train_path,
                '--cd', cd_path,
                '-i', '5',
                '-T', '4',
                '-r', '0',
                '--use-best-model', 'false',
                )
    test0_path = yatest.common.test_output_path('test0.txt')
    open(test0_path, 'wt').write('')
    with pytest.raises(yatest.common.ExecutionError):
        yatest.common.execute(fit_stem + (
            '-t', ','.join((test_input_path, test0_path))
        ))


@pytest.mark.parametrize('loss_function', ['RMSE', 'QueryRMSE'])
def test_multiple_eval_sets(loss_function):
    num_tests = 5
    train_path = data_file('querywise', 'train')
    cd_path = data_file('querywise', 'train.cd.query_id')
    test_input_path = data_file('querywise', 'test')
    eval_path = yatest.common.test_output_path('test.eval')
    test_paths = split_test_to(num_tests, test_input_path)
    cmd = (CATBOOST_PATH, 'fit',
           '--loss-function', loss_function,
           '-f', train_path,
           '-t', ','.join(test_paths),
           '--column-description', cd_path,
           '-i', '5',
           '-T', '4',
           '-r', '0',
           '--use-best-model', 'false',
           '--eval-file', eval_path,
           )
    yatest.common.execute(cmd)
    return [local_canonical_file(eval_path)]


def test_multiple_eval_sets_err_log():
    num_tests = 3
    train_path = data_file('querywise', 'train')
    cd_path = data_file('querywise', 'train.cd.query_id')
    test_input_path = data_file('querywise', 'test')
    test_err_log_path = yatest.common.test_output_path('test-err.log')
    json_log_path = yatest.common.test_output_path('json.log')
    test_paths = split_test_to(num_tests, test_input_path)
    cmd = (CATBOOST_PATH, 'fit',
           '--loss-function', 'RMSE',
           '-f', train_path,
           '-t', ','.join(test_paths),
           '--column-description', cd_path,
           '-i', '5',
           '-T', '4',
           '-r', '0',
           '--test-err-log', test_err_log_path,
           '--json-log', json_log_path,
           )
    yatest.common.execute(cmd)
    return [local_canonical_file(test_err_log_path),
            local_canonical_file(remove_time_from_json(json_log_path))]


# Cast<float>(CityHash('Quvena')) is QNaN
# Cast<float>(CityHash('Sineco')) is SNaN
@pytest.mark.parametrize('cat_value', ['Normal', 'Quvena', 'Sineco'])
def test_const_cat_feature(cat_value):
    def make_a_set(nrows, value):
        label = np.random.randint(0, nrows, [nrows, 1])
        feature = np.full([nrows, 1], value, dtype='|S{}'.format(len(value)))
        return np.concatenate([label, feature], axis=1)

    cd_path = yatest.common.test_output_path('cd.txt')
    np.savetxt(cd_path, [[0, 'Target'], [1, 'Categ']], fmt='%s', delimiter='\t')

    train_path = yatest.common.test_output_path('train.txt')
    np.savetxt(train_path, make_a_set(10, cat_value), fmt='%s', delimiter='\t')

    test_path = yatest.common.test_output_path('test.txt')
    np.savetxt(test_path, make_a_set(10, cat_value), fmt='%s', delimiter='\t')

    eval_path = yatest.common.test_output_path('eval.txt')

    cmd = (CATBOOST_PATH, 'fit',
           '--loss-function', 'RMSE',
           '-f', train_path,
           '-t', test_path,
           '--column-description', cd_path,
           '-i', '5',
           '-T', '4',
           '-r', '0',
           '--eval-file', eval_path,
           )
    with pytest.raises(yatest.common.ExecutionError):
        yatest.common.execute(cmd)


def test_model_metadata():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '-i', '2',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '-w', '0.1',
        '--set-metadata-from-freeargs',
        'A', 'A',
        'BBB', 'BBB',
        'CCC', 'A'
    )
    yatest.common.execute(cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'metadata', 'set',
        '-m', output_model_path,
        '--key', 'CCC',
        '--value', 'CCC'
    )
    yatest.common.execute(calc_cmd)

    calc_cmd = (
        CATBOOST_PATH,
        'metadata', 'set',
        '-m', output_model_path,
        '--key', 'CCC',
        '--value', 'CCC'
    )
    yatest.common.execute(calc_cmd)

    py_catboost = catboost.CatBoost(model_file=output_model_path)
    assert 'A' == py_catboost.metadata_['A']
    assert 'BBB' == py_catboost.metadata_['BBB']
    assert 'CCC' == py_catboost.metadata_['CCC']


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_learning_rate_auto_set(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--use-best-model', 'false',
        '--loss-function', 'Logloss',
        '-f', data_file('adult', 'train_small'),
        '-t', data_file('adult', 'test_small'),
        '--column-description', data_file('adult', 'train.cd'),
        '--boosting-type', boosting_type,
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--od-type', 'Iter',
        '--od-wait', '1',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_paths_with_dsv_scheme():
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', 'dsv://' + data_file('querywise', 'train'),
        '-t', 'dsv://' + data_file('querywise', 'test'),
        '--column-description', 'dsv://' + data_file('querywise', 'train.cd'),
        '--boosting-type', 'Ordered',
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '-m', output_model_path,
        '--eval-file', output_eval_path,
        '--use-best-model', 'false',
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(output_eval_path)]


def test_skip_train():
    learn_error_path = yatest.common.test_output_path('learn_error.tsv')
    test_error_path = yatest.common.test_output_path('test_error.tsv')
    json_log_path = yatest.common.test_output_path('json_log.json')
    cmd = (
        CATBOOST_PATH,
        'fit',
        '--loss-function', 'QueryRMSE',
        '-f', data_file('querywise', 'train'),
        '-t', data_file('querywise', 'test'),
        '--column-description', data_file('querywise', 'train.cd'),
        '-i', '20',
        '-T', '4',
        '-r', '0',
        '--custom-metric', 'QueryAverage:top=2;hints=skip_train~true',
        '--learn-err-log', learn_error_path,
        '--test-err-log', test_error_path,
        '--use-best-model', 'false',
        '--json-log', json_log_path
    )
    yatest.common.execute(cmd)

    return [local_canonical_file(learn_error_path),
            local_canonical_file(test_error_path),
            local_canonical_file(remove_time_from_json(json_log_path))]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
def test_group_weight(boosting_type):
    output_model_path = yatest.common.test_output_path('model.bin')
    output_eval_path = yatest.common.test_output_path('test.eval')

    def run_catboost(train_path, test_path, cd_path, eval_path):
        cmd = (
            CATBOOST_PATH,
            'fit',
            '--loss-function', 'YetiRank',
            '-f', data_file('querywise', train_path),
            '-t', data_file('querywise', test_path),
            '--column-description', data_file('querywise', cd_path),
            '--boosting-type', boosting_type,
            '-i', '10',
            '-T', '4',
            '-r', '0',
            '-m', output_model_path,
            '--eval-file', eval_path,
        )
        yatest.common.execute(cmd)

    output_eval_path_first = yatest.common.test_output_path('test_first.eval')
    output_eval_path_second = yatest.common.test_output_path('test_second.eval')
    run_catboost('train', 'test', 'train.cd', output_eval_path_first)
    run_catboost('train.const_group_weight', 'test.const_group_weight', 'train.cd.group_weight', output_eval_path_second)
    assert filecmp.cmp(output_eval_path_first, output_eval_path_second)

    run_catboost('train', 'test', 'train.cd.group_weight', output_eval_path)
    return [local_canonical_file(output_eval_path)]


@pytest.mark.parametrize('boosting_type', BOOSTING_TYPE)
@pytest.mark.parametrize('loss_function', ['QueryRMSE', 'RMSE'])
def test_group_weight_and_object_weight(boosting_type, loss_function):
    def run_catboost(train_path, test_path, cd_path, eval_path):
        cmd = (
            CATBOOST_PATH,
            'fit',
            '--loss-function', loss_function,
            '-f', data_file('querywise', train_path),
            '-t', data_file('querywise', test_path),
            '--column-description', data_file('querywise', cd_path),
            '--boosting-type', boosting_type,
            '-i', '10',
            '-T', '4',
            '-r', '0',
            '--eval-file', eval_path,
        )
        yatest.common.execute(cmd)

    output_eval_path_first = yatest.common.test_output_path('test_first.eval')
    output_eval_path_second = yatest.common.test_output_path('test_second.eval')
    run_catboost('train', 'test', 'train.cd.group_weight', output_eval_path_first)
    run_catboost('train', 'test', 'train.cd.weight', output_eval_path_second)
    assert filecmp.cmp(output_eval_path_first, output_eval_path_second)
