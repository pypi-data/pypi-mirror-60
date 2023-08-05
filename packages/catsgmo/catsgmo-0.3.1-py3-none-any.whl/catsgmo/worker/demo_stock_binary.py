import datetime
import sys
import requests
import re
import json
import time
from catsgmo.worker.output import worker_out
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import selenium
from catscore.http.request import CatsRequest
from catscore.http.web_driver import CatsWebDriver
from catscore.lib.logger import CatsLogging as logging
from catscore.lib.time import get_today_date, get_current_time
from catsgmo.site.demo_stock_binary import DemoGMOStockBinarySite

class DemoGMOStockBinaryWorkerError(RuntimeError):
    pass
    
class DemoGMOStockBinaryWorker:
    @classmethod
    def start(cls, web_driver_json: str, type: str, output_folder_path: str, error_count_max:int=4):
        gmo = DemoGMOStockBinarySite(request=CatsRequest(), web_driver=CatsWebDriver.instance(json_path=web_driver_json))
        gmo.init()
        error_count = 0
        while True:
            try:
                result = None
                if type == "us":
                    result = gmo.all_round_info("米国30")
                else:
                    result = gmo.all_round_info("日本225")
                jstr = result.to_json(ensure_ascii=False)
                worker_out(output_folder_path=output_folder_path, jstr=jstr, function_name=f"gmo_demo_stock_binary_{type}")
                error_count = 0
            except Exception:
                if error_count > error_count_max:
                    raise DemoGMOStockBinaryWorkerError(sys.exc_info())
                else:
                    error_count = error_count + 1
                    gmo.close()
                    gmo = DemoGMOStockBinarySite(request=CatsRequest(), web_driver=CatsWebDriver.instance(json_path=web_driver_json))
                    gmo.init()
                    message = f"DemoGMOStockBinaryWorker error count is {error_count}, {sys.exc_info()}"
                    logging.notify(message)
                    logging.warn(message)
        