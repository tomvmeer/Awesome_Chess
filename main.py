import os
from multiprocessing import Pool
import config

path = config.load_config('python_path')


def run(process):
    os.system(f'{path} {process}')


if __name__ == '__main__':
    processes = ('network_process.py', 'game_process.py')
    pool = Pool(processes=2)
    pool.map(run, processes)
