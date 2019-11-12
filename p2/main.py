import os
from multiprocessing import Pool


def run(process):
    os.system(f'C:/ProgramData/Anaconda3/python {process}')


if __name__ == '__main__':
    processes = ('network_process.py', 'game_process.py')
    pool = Pool(processes=2)
    pool.map(run, processes)
