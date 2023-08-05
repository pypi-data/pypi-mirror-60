""""
Run agent training and testing.

Author: Nikolay Lysenko
"""


import argparse
import datetime
import os
from pkg_resources import resource_filename
from typing import Any, Dict

import numpy as np
import yaml

from rlmusician.agent import (
    CounterpointEnvAgent,
    create_actor_model, find_n_weights_by_params, optimize_with_cem
)
from rlmusician.environment import CounterpointEnv, Piece


def evaluate_agent_weights(
        flat_weights: np.ndarray,
        piece_params: Dict[str, Any],
        environment_params: Dict[str, Any],
        agent_params: Dict[str, Any]
) -> float:
    """
    Evaluate weights of actor model for an agent.

    :param flat_weights:
        1D array of weights to be evaluated
    :param piece_params:
        settings of `Piece` instance
    :param environment_params:
        settings of environment
    :param agent_params:
        settings of agent
    :return:
        reward earned by the agent with the given weights
    """
    piece = Piece(**piece_params)
    env = CounterpointEnv(piece, **environment_params)
    agent = CounterpointEnvAgent(**agent_params)
    agent.set_weights(flat_weights)
    reward = agent.run_episode(env)
    return reward


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Music composition with RL')
    parser.add_argument(
        '-c', '--config_path', type=str, default=None,
        help='path to configuration file'
    )
    parser.add_argument(
        '-p', '--populations', type=int, default=15,
        help='number of populations for agent training'
    )
    parser.add_argument(
        '-e', '--episodes', type=int, default=3,
        help='number of episodes for testing agent after its training'
    )
    cli_args = parser.parse_args()
    return cli_args


def main() -> None:
    """Parse CLI arguments, train agent, and test it."""
    cli_args = parse_cli_args()

    default_config_path = 'configs/default_config.yml'
    default_config_path = resource_filename(__name__, default_config_path)
    config_path = cli_args.config_path or default_config_path
    with open(config_path) as config_file:
        settings = yaml.safe_load(config_file)

    results_dir = settings['piece']['rendering_params']['dir']
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)

    piece = Piece(**settings['piece'])
    env = CounterpointEnv(piece, **settings['environment'])
    env.verbose = True
    actions = [
        2 * 7 + 4,
        4 * 7 + 4,
        4 * 7 + 3,
        4 * 7 + 2,
        4 * 7 + 4,
        2 * 7 + 5,
        2 * 7 + 6,
        2 * 7 + 2,
        4 * 7 + 2,
        0 * 7 + 2,
        4 * 7 + 2,
        2 * 7 + 2,
        3 * 7 + 1,
        2 * 7 + 2,
        # 2 * 7 + 4,
    ]
    for action in actions:
        _, reward, _, _ = env.step(action)
    print(reward)
    env.render()


if __name__ == '__main__':
    main()