import os
from catscore.lib.time import get_today_date, get_current_time
from catscore.lib.logger import CatsLogging as logging
import pathlib
import shutil

def worker_out(output_folder_path: str, jstr: str, function_name: str, zip:bool=True):
    # output init
    daily_folder_path = f"{output_folder_path}/{function_name}/{get_today_date()}"
    zip_daily_folder_path = daily_folder_path + ".zip"
    worker_out_path = daily_folder_path + f"/{function_name}_{get_current_time()}.json"
    logging.info(f"daily_folder_path: {daily_folder_path}")
    logging.info(f"zip_daily_folder_path: {zip_daily_folder_path}")
    logging.info(f"worker_out_path: {worker_out_path}")
    # check daily_folder
    daily_folder = pathlib.Path(daily_folder_path)
    if not daily_folder.exists():
        logging.info(f"daily_folder_path: mkdir {daily_folder_path}")
        daily_folder.mkdir(parents=True)
    # output json
    with open(worker_out_path, 'w') as f:
        f.write(jstr)
    # zip daily_folder
    shutil.make_archive(daily_folder_path, 'zip', root_dir=daily_folder_path)
    
    
    
    
    