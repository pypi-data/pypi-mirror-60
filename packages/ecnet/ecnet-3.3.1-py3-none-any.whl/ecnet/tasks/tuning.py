#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ecnet/tasks/tuning.py
# v.3.3.1
# Developed in 2020 by Travis Kessler <travis.j.kessler@gmail.com>
#
# Contains functions/fitness functions for tuning hyperparameters
#

# stdlib. imports
from multiprocessing import set_start_method
from os import name

# 3rd party imports
from ecabc.abc import ABC

# ECNet imports
from ecnet.utils.data_utils import DataFrame
from ecnet.utils.logging import logger
from ecnet.utils.server_utils import default_config, train_model


def tune_hyperparameters(df: DataFrame, vars: dict, num_employers: int,
                         num_iterations: int, num_processes: int = 1,
                         shuffle: str = None, split: list = None,
                         validate: bool = True, eval_set: str = None,
                         eval_fn: str = 'rmse', epochs: int = 300) -> dict:
    '''Tunes neural network learning/architecture hyperparameters

    Args:
        df (ecnet.utils.data_utils.DataFrame): currently loaded data
        vars (dict): ecnet.Server._vars variables
        num_employers (int): number of employer bees
        num_iterations (int): number of search cycles for the colony
        num_processes (int): number of parallel processes to utilize
        shuffle (str): shuffles `train` or `all` sets if not None
        split (list): if shuffle is True, [learn%, valid%, test%]
        validate (bool): if True, uses periodic validation; otherwise, no
        eval_set (str): set used to evaluate bee performance; `learn`, `valid`,
            `train`, `test`, None (all sets)
        eval_fn (str): error function used to evaluate bee performance; `rmse`,
            `mean_abs_error`, `med_abs_error`
        epochs (int): number of training epochs per bee ANN (def: 300)

    Returns:
        dict: tuned hyperparameters
    '''

    if name != 'nt':
        set_start_method('spawn', force=True)

    logger.log('info', 'Tuning architecture/learning hyperparameters',
               call_loc='TUNE')
    logger.log('debug', 'Arguments:\n\t| num_employers:\t{}\n\t| '
               'num_iterations:\t{}\n\t| shuffle:\t\t{}\n\t| split:'
               '\t\t{}\n\t| validate:\t\t{}\n\t| eval_set:\t\t{}\n\t'
               '| eval_fn:\t\t{}'.format(
                   num_employers, num_iterations, shuffle, split, validate,
                   eval_set, eval_fn
               ), call_loc='TUNE')

    fit_fn_args = {
        'df': df,
        'shuffle': shuffle,
        'num_processes': num_processes,
        'split': split,
        'validate': validate,
        'eval_set': eval_set,
        'eval_fn': eval_fn,
        'hidden_layers': vars['hidden_layers'],
        'epochs': epochs
    }

    value_ranges = [
        ('float', (1e-9, 1e-4)),            # Learning rate decay
        ('float', (1e-5, 0.1)),             # Learning rate
        ('int', (1, len(df.learn_set))),    # Batch size
        ('int', (64, 1024))                 # Patience
    ]

    for _ in range(len(vars['hidden_layers'])):
        value_ranges.append(('int', (1, len(df._input_names))))

    abc = ABC(
        tune_fitness_function,
        num_employers=num_employers,
        value_ranges=value_ranges,
        args=fit_fn_args,
        processes=num_processes
    )

    abc._logger.stream_level = logger.stream_level
    if logger.file_level != 'disable':
        abc._logger.log_dir = logger.log_dir
        abc._logger.file_level = logger.file_level
    abc._logger.default_call_loc('TUNE')
    abc.create_employers()
    for i in range(num_iterations):
        logger.log('info', 'Iteration {}'.format(i + 1), call_loc='TUNE')
        abc.run_iteration()
        logger.log('info', 'Best Performer: {}, {}'.format(
            abc.best_performer[2], {
                'decay': abc.best_performer[1][0],
                'learning_rate': abc.best_performer[1][1],
                'batch_size': abc.best_performer[1][2],
                'patience': abc.best_performer[1][3],
                'hidden_layers': abc.best_performer[1][4:]
            }
        ), call_loc='TUNE')
    params = abc.best_performer[1]
    vars['decay'] = params[0]
    vars['learning_rate'] = params[1]
    vars['batch_size'] = params[2]
    vars['patience'] = params[3]
    for l_idx in range(len(vars['hidden_layers'])):
        vars['hidden_layers'][l_idx][0] = params[4 + l_idx]
    return vars


def tune_fitness_function(params: dict, **kwargs):
    '''Fitness function used by ABC

    Args:
        params (dict): bee hyperparams
        kwargs (dict): additional arguments

    Returns:
        float: error of NN with supplied hyperparams
    '''

    vars = default_config()
    vars['decay'] = params[0]
    vars['learning_rate'] = params[1]
    vars['batch_size'] = params[2]
    vars['patience'] = params[3]
    vars['hidden_layers'] = kwargs['hidden_layers']
    vars['epochs'] = kwargs['epochs']
    for l_idx in range(len(vars['hidden_layers'])):
        vars['hidden_layers'][l_idx][0] = params[4 + l_idx]

    df = kwargs['df']
    if kwargs['shuffle'] is not None:
        df.shuffle(kwargs['shuffle'], kwargs['split'])
    sets = df.package_sets()

    return train_model(sets, vars, kwargs['eval_set'], kwargs['eval_fn'],
                       validate=kwargs['validate'], save=False)[0]
