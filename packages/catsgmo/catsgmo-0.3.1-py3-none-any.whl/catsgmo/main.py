import argparse
from catscore.http.request import CatsRequest
from catscore.lib.logger import CatsLogging as logging
from catscore.db.mysql import MySQLConf
from catsgmo.worker.demo_stock_binary import DemoGMOStockBinaryWorker

def main():
    parser = argparse.ArgumentParser(description="cats gmo")

    # args params
    parser.add_argument('-lg', '--log', help="log configuration file", required=True)
    parser.add_argument('-wd', '--webdriver', help="web_driver configuration file", required=True)
    parser.add_argument('-op', '--output', help="output folder path", required=True)
    parser.add_argument('--stock_binary_worker',  nargs='*', choices=['jp','us'],  help="stock_binary functions")
    args = parser.parse_args()
    print(args)

    # init
    logging.init_from_json(args.log)
    logging.info("catsgmo start")
    
    if args.stock_binary_worker:
        for arg in args.stock_binary_worker:
            DemoGMOStockBinaryWorker.start(web_driver_json=args.webdriver, type=arg, output_folder_path=args.output)
    
    # close 

if __name__ == "__main__":
    main()