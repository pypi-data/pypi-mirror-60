from unittest import mock

import kerastuner
import pytest
import tensorflow as tf

from autokeras.engine import tuner as tuner_module
from tests import utils


@pytest.fixture(scope='module')
def tmp_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('test_auto_model')


@mock.patch('kerastuner.engine.base_tuner.BaseTuner.__init__')
@mock.patch('kerastuner.engine.base_tuner.BaseTuner.search')
@mock.patch('tensorflow.keras.Model.fit')
def test_add_early_stopping(fit_fn, base_tuner_search, init, tmp_dir):
    graph = utils.build_graph()
    tuner = tuner_module.AutoTuner(oracle=mock.Mock(), hypermodel=graph)
    tuner.hypermodel = graph
    tuner.oracle = mock.Mock()
    tuner.directory = tmp_dir
    tuner.project_name = ''
    hp = kerastuner.HyperParameters()
    trial = mock.Mock()
    trial.hyperparameters = hp
    oracle = mock.Mock()
    oracle.get_best_trials.return_value = (trial,)
    tuner.oracle = oracle

    tuner.search()

    callbacks = base_tuner_search.call_args_list[0][1]['callbacks']
    assert any([isinstance(callback, tf.keras.callbacks.EarlyStopping)
                for callback in callbacks])


@mock.patch('kerastuner.engine.base_tuner.BaseTuner.__init__')
def test_overwrite_init(base_tuner_init, tmp_dir):
    tuner_module.AutoTuner(
        oracle=mock.Mock(),
        hypermodel=lambda hp: None,
        directory=tmp_dir)

    assert not base_tuner_init.call_args_list[0][1]['overwrite']


@mock.patch('kerastuner.engine.base_tuner.BaseTuner.__init__')
@mock.patch('kerastuner.engine.base_tuner.BaseTuner.search')
@mock.patch('tensorflow.keras.Model.fit')
def test_overwrite_search(fit_fn, base_tuner_search, init, tmp_dir):
    graph = utils.build_graph()
    tuner = tuner_module.AutoTuner(oracle=mock.Mock(), hypermodel=graph)
    tuner.hypermodel = graph
    tuner.oracle = mock.Mock()
    tuner.directory = tmp_dir
    tuner.project_name = ''
    hp = kerastuner.HyperParameters()
    trial = mock.Mock()
    trial.hyperparameters = hp
    oracle = mock.Mock()
    oracle.get_best_trials.return_value = (trial,)
    tuner.oracle = oracle

    tuner.search()

    assert tuner._finished
