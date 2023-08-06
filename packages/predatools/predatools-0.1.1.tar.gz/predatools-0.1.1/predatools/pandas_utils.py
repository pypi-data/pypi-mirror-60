import multiprocessing
from multiprocessing import Pool
import pandas as pd
from tqdm import tqdm_notebook as tqdm


def parallel_process_df(func, args, n_processes = multiprocessing.cpu_count()-1):
    concat_result = pd.DataFrame()
    p = Pool(n_processes)
    res_list = []
    
    with tqdm(total = len(args)) as pbar:
        for i, res in tqdm(enumerate(p.imap_unordered(func, args))):
            pbar.update()
            concat_result = pd.concat([concat_result,res])
    pbar.close()
    p.close()
    p.join()
    return concat_result