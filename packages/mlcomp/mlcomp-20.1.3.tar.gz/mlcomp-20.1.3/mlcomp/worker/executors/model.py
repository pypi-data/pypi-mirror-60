import os
from os.path import join
import shutil
from pathlib import Path
import sys

import safitty
import torch

from catalyst.dl.core import Experiment
from catalyst import utils
from catalyst.dl.utils.trace import trace_model
from catalyst.utils import import_experiment_and_runner

from mlcomp import TASK_FOLDER, MODEL_FOLDER
from mlcomp.db.models import Model
from mlcomp.db.providers import TaskProvider, ModelProvider, \
    ProjectProvider
from mlcomp.utils.misc import now
from mlcomp.utils.config import Config
from mlcomp.worker.executors import Executor


def trace_model_from_checkpoint(logdir, logger, method_name='forward',
                                file='best'):
    config_path = f'{logdir}/configs/_config.json'
    checkpoint_path = f'{logdir}/checkpoints/{file}.pth'
    logger.info('Load config')
    config = safitty.load(config_path)
    if 'distributed_params' in config:
        del config['distributed_params']

    # Get expdir name
    # noinspection SpellCheckingInspection,PyTypeChecker
    # We will use copy of expdir from logs for reproducibility
    expdir_name = config['args']['expdir']
    logger.info(f'expdir_name from args: {expdir_name}')

    sys.path.insert(0, os.path.abspath(join(logdir, '../')))

    expdir_from_logs = os.path.abspath(join(logdir, '../', expdir_name))

    logger.info(f'expdir_from_logs: {expdir_from_logs}')
    logger.info('Import experiment and runner from logdir')

    ExperimentType, RunnerType = \
        import_experiment_and_runner(Path(expdir_from_logs))
    experiment: Experiment = ExperimentType(config)

    logger.info(f'Load model state from checkpoints/{file}.pth')
    model = experiment.get_model(next(iter(experiment.stages)))
    checkpoint = utils.load_checkpoint(checkpoint_path)
    utils.unpack_checkpoint(checkpoint, model=model)

    device = 'cpu'
    stage = list(experiment.stages)[0]
    loader = 0
    mode = 'eval'
    requires_grad = False
    opt_level = None

    runner: RunnerType = RunnerType()
    runner.model, runner.device = model, device

    batch = experiment.get_native_batch(stage, loader)

    logger.info('Tracing')
    traced = trace_model(
        model,
        runner,
        batch,
        method_name=method_name,
        mode=mode,
        requires_grad=requires_grad,
        opt_level=opt_level,
        device=device,
    )

    logger.info('Done')
    return traced


@Executor.register
class ModelAdd(Executor):
    def __init__(
            self,
            name: str,
            project: int,
            fold: int,
            train_task: int = None,
            child_task: int = None,
            file: str = None,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.train_task = train_task
        self.name = name
        self.child_task = child_task
        self.project = project
        self.file = file
        self.fold = fold

    def work(self):
        project = ProjectProvider(self.session).by_id(self.project)

        self.info(f'Task = {self.train_task} child_task: {self.child_task}')

        model = Model(
            created=now(),
            name=self.name,
            project=self.project,
            equations='',
            fold=self.fold
        )

        provider = ModelProvider(self.session)
        if self.train_task:
            task_provider = TaskProvider(self.session)
            task = task_provider.by_id(self.train_task)
            model.score_local = task.score

            task_dir = join(TASK_FOLDER, str(self.child_task or task.id))
            src_log = f'{task_dir}/log'
            models_dir = join(MODEL_FOLDER, project.name)
            os.makedirs(models_dir, exist_ok=True)

            model_path_tmp = f'{src_log}/traced.pth'
            traced = trace_model_from_checkpoint(src_log, self, file=self.file)

            model_path = f'{models_dir}/{model.name}.pth'
            model_weight_path = f'{models_dir}/{model.name}_weight.pth'
            torch.jit.save(traced, model_path_tmp)
            shutil.copy(model_path_tmp, model_path)
            file = self.file = 'best_full'
            shutil.copy(f'{src_log}/checkpoints/{file}.pth',
                        model_weight_path)

        provider.add(model)

    @classmethod
    def _from_config(
            cls, executor: dict, config: Config, additional_info: dict
    ):
        return ModelAdd(
            name=executor['name'],
            project=executor['project'],
            train_task=executor['task'],
            child_task=executor['child_task'],
            fold=executor['fold'],
            file=executor['file']
        )


__all__ = ['ModelAdd', 'trace_model_from_checkpoint']
