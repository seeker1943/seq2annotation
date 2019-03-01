import os

import numpy as np
import ray
import ray.tune as tune
from seq2annotation.trainer.train_model import train_model
from seq2annotation.algorithms.BiLSTM_CRF_model import BilstmCrfModel

ray.init(num_gpus=1)

cwd = os.getcwd()


def train_func(config, reporter):
    evaluate_result, export_results = train_model(
        data_dir=os.path.join(cwd, './data'), result_dir=os.path.join(cwd, './results'),
        train_spec={'max_steps': None},
        hook={
            'stop_if_no_increase': {
                'min_steps': 10000,
                'run_every_secs': 600,
                'max_steps_without_increase': 100000
            }
        },
        model=BilstmCrfModel,
        optimizer_params={'learning_rate': config['momentum']},
        **BilstmCrfModel.default_params(),
    )

    reporter(mean_accuracy=evaluate_result['correct_rate'])


all_trials = tune.run_experiments({
    "my_experiment": {
        "run": train_func,
        "stop": {"mean_accuracy": 0.96},
        "config": {"momentum": tune.grid_search(np.linspace(0.01, 2.0, num=24))}
    }
})

print(all_trials)
