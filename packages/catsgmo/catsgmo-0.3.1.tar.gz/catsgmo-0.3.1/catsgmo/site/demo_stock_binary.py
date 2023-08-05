import datetime
import sys
import requests
import re
import json
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import selenium
from catscore.http.request import CatsRequest
from catscore.http.web_driver import CatsWebDriver
from catscore.lib.logger import CatsLogging as logging
from catscore.lib.time import get_today_date, get_current_time
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List

class InitPageError(RuntimeError):
    pass

class TransitionFailedError(RuntimeError):
    pass

class DataConsistencyError(RuntimeError):
    pass

@dataclass
@dataclass_json
class StockPrice:
    time: str
    openPrice: str
    highPrice: str
    lowPrice: str
    closePrice: str

@dataclass
@dataclass_json
class Order:
    buy: str
    sell: str
    payout_price: str

@dataclass
@dataclass_json
class OrderInfo:
    put: Order
    pull: Order
    
@dataclass
@dataclass_json
class Condition:
	target_price: str
	selector_value: str
 
@dataclass
@dataclass_json
class ConditionList:
	conditions: List[Condition]
 
@dataclass
@dataclass_json
class ConditionInfo:
    trading_name: str
    timestamp: str
    round_date: str
    round_name: str
    condition: Condition
    order_info: OrderInfo

@dataclass
@dataclass_json
class RoundInfo:
    trading_name: str
    timestamp: str
    round_date: str
    round_name: str
    condition_infos: List[ConditionInfo]
    stock_price: StockPrice

@dataclass
@dataclass_json
class AllRoundInfo:
    round_infos: List[RoundInfo]

class DemoGMOStockBinarySite:
    order_url = "https://demo.click-sec.com/ixop/order.do"
    
    def __init__(self, request: CatsRequest, web_driver: CatsWebDriver):
        self.request = request
        self.web_driver = web_driver
        
    def init(self):
        self._init_page(click_skip=True)

    def _init_page(self, click_skip, timeout=1):
        """[ページの初期化]
        
        Arguments:
            click_skip {[type]} -- [description]
        """
        self.web_driver.move(self.order_url)
        if click_skip:
            # check
            error_count = 0
            skipped = 4
            while True:
                try:
                    self.web_driver.wait_rendering_by_class('joyride-tooltip__button')
                    self.web_driver.wait_rendering_by_class('round-list')
                    for i in range(skipped):
                        logging.info(f"_init_page skip {i}")
                        button = self.web_driver.driver.find_elements_by_css_selector(".joyride-tooltip__button.joyride-tooltip__button--primary")[0]
                        button.click()
                        time.sleep(1)
                        skipped = skipped -1
                    logging.info("_init_page success")
                    return True
                except:
                    if error_count < 3:
                        logging.info(f"__init_page error count is {error_count}")
                        error_count = error_count + 1
                        time.sleep(timeout)
                    else:
                        logging.info(f"__init_page is failed: {sys.exc_info()}")
                        raise InitPageError(f"__init_page is failed: {sys.exc_info()}")
    
    def close(self):
        """[close DemoGMOStockBinary]
        """
        self.web_driver.close()
        self.request.close()

    def reload(self):
        logging.info("DemoGMOStockBinary reload")
        self.web_driver.reload()

    def is_open(self):
        """[ToDo: check market is open or close]
        """
        pass

    @property
    def trading_name(self):
        """[ 現在の銘柄を取得]
        
        Returns:
            [type] -- [description]
        """
        name = self.web_driver.html.find('button', {'class': 'currency-list-button on'}).text
        logging.info(f"trading_name is {name}")
        return name

    def transition_trading(self, trading_name):
        """[銘柄を変更]
        
        Arguments:
            id {[trading_name]} -- [日本225 or 米国30]
        """
        current_trading_name = self.trading_name
        if current_trading_name != trading_name: # 遷移が必要ない場合は遷移しない
            logging.info(f"transition_trading transition {current_trading_name} to {trading_name}")
            if trading_name == "米国30":
                id = 1
            else:
                id = 0
            button = self.web_driver.driver.find_elements_by_css_selector(".currency-list-button")[id]
            button.click()

            # check
            error_count = 0
            while True:
                current_trading_name = self.trading_name
                logging.info(f"transition_trading transitioned {current_trading_name}")
                if trading_name == current_trading_name:
                    return True
                elif error_count == 4:
                    raise TransitionFailedError("transition_trading is failed")
                else:
                    error_count = error_count + 1
                    logging.info(f"transition_trading error count is : {error_count}")

    @property
    def round_list(self):
        """[ラウンド一覧を取得]
        
        Returns:
            [type] -- [description]
        """
        round_list = self.web_driver.html.find('div', {'class': 'round-list'})
        buttons = round_list.findAll('button')
        round_list = list(filter(lambda x: x[0][0] == 'round-list-button', map(lambda x: (x.get("class"), x), buttons)))
        logging.info(f"round_list: {round_list}")
        return round_list

    @property
    def accept_round_list(self):
        """[Acceptステータスのラウンド一覧を取得]
        
        Returns:
            [type] -- [description]
        """
        accept_round_list = list(filter(lambda x: (x[0][1] == 'ACCEPT'), self.round_list))
        # or END_ACCEPT
        logging.info(f"accept_round_list is {accept_round_list}")
        return accept_round_list
    
    @property
    def accept_and_endaccept_round_list(self):
        """[Accept/END_ACCEPTステータスのラウンド一覧を取得]
        
        Returns:
            [type] -- [description]
        """
        accept_round_list = list(filter(lambda x: (x[0][1] == 'ACCEPT') or (x[0][1] == 'END_ACCEPT'), self.round_list))
        logging.info(f"accept_and_endaccept_round_list is {accept_round_list}")
        return accept_round_list

    def transtion_accept_round(self, round, include_endaccept):
        """[acceptステータスのラウンドを移動]
        
        Arguments:
            round {[type]} -- [first or second]
        """
        if round == "first":
            round_id = 0
        elif round == "second":
            round_id = 1
        else:
            round_id = 0
        accept_round_list = None
        if include_endaccept:
            accept_round_list = self.accept_and_endaccept_round_list
        else:
            accept_round_list = self.accept_round_list
        if len(accept_round_list) < 1:
            raise TransitionFailedError(f"transtion_accept_round {round} round is not open")
        elif len(accept_round_list) == 1 and round == "second":
            raise TransitionFailedError(f"transtion_accept_round {round} round second is not open")
        transition_round = accept_round_list[round_id][1]
        current_round = self.round
        logging.info(f"transtion_accept_round: current_round is {current_round.text}, will transition_round is {transition_round.text}")
        if current_round.text != transition_round.text:
            logging.info("transtion_accept_round: transition round")
            button = None
            if include_endaccept:
                b1 = self.web_driver.driver.find_elements_by_css_selector(".round-list-button.END_ACCEPT")
                logging.info(f"b1: {b1}")
                b2 = self.web_driver.driver.find_elements_by_css_selector(".round-list-button.ACCEPT")
                logging.info(f"b2: {b2}")
                buttons = b1 + b2
                logging.info(f"buttons: {buttons}")
                button = buttons[round_id]
            else:
                button = self.web_driver.driver.find_elements_by_css_selector(".round-list-button.ACCEPT")[round_id]
            button.click()
        # check
        for i in range(4):
            transitioned_round = self.round
            if transition_round.text == transitioned_round.text:
                logging.info(f"transtion_accept_round: transitioned_round is {transitioned_round.text}")
                return True
            else:
                logging.info(f"transtion_accept_round: error count is {i}")
                time.sleep(1)
        raise TransitionFailedError("transtion_accept_round is failed")

    @property
    def round(self):
        """[現在のラウンドを取得]
        """
        round = list(filter(lambda x: (x[0][-1] == 'on'), self.round_list))
        if len(round) != 1:
            raise RuntimeError(f"round: current round len are {round}")
        else:
            logging.info(f"round: {round[0][1]}")
            return round[0][1]

    @property
    def stock_price(self) -> StockPrice:
        """[現在の株価情報を取得]

        Returns:
            [type] -- [description]
        """
        trading_name = self.trading_name
        if trading_name == "日本225":
            stock_price_url = "https://demo.click-sec.com/boquote/api/v3/chart?underlierCd=000001&count=1&type=MIN_1"
        elif trading_name == "米国30":
            stock_price_url = "https://demo.click-sec.com/boquote/api/v3/chart?underlierCd=000002&count=1&type=MIN_1"
        json = self.request.get(stock_price_url, response_content_type="json").content[0]
        result = StockPrice(
            time=json["time"],
            openPrice=json["open"],
            highPrice=json["high"],
            lowPrice=json["low"],
            closePrice=json["close"])
        logging.debug(f"stock_price: {result}")
        return result

    @property
    def order_info(self) -> OrderInfo:
        """[オーダ情報を取得]
        
        Returns:
            [type] -- [description]
        """
        def __parse_oder_panel(order_panel) -> Order:
            buy = order_panel.find('span', {'class': 'order-buy-price'}).text
            sell = order_panel.find('span', {'class': 'order-sell-price'}).text
            payout_price = order_panel.find('span', {'class': 'order-payout-price'}).text
            return Order(buy=buy, sell=sell, payout_price=payout_price)

        trade_panel = self.web_driver.html.find('div', {'class': 'trade-panel'})
        panel_put = __parse_oder_panel(trade_panel.find('div', {'class': 'panel-put'}))
        panel_call = __parse_oder_panel(trade_panel.find('div', {'class': 'panel-call'}))
        r = OrderInfo(put=panel_put, call=panel_call)
        logging.debug(f"order_info: {r}")
        return r

    @property
    def condition_list(self) -> ConditionList:
        """[権利行使価格一覧を取得]
        """
        target_selector = self.web_driver.html.find('select', {'class': 'select-strike-price'})
        result = ConditionList(conditions=list(map(lambda selector: Condition(target_price=selector.text, selector_value=selector["value"]), target_selector)))
        logging.debug(f"condition_list: {result}")
        return result

    @property
    def condition(self) -> Condition:
        selectable_selector = Select(self.web_driver.driver.find_element_by_class_name('select-strike-price'))
        result = Condition(target_price=selectable_selector.first_selected_option.text, selector_value=selectable_selector.first_selected_option.get_property("value"))
        logging.debug(f"condition: {result}")
        return result

    def transion_condition(self, value: str):
        """[summary]
        
        Arguments:
            value {[str]} -- [From 1 to 7]
        """
        before_value = self.condition.selector_value
        if before_value != value:
            logging.debug("transion_condition")
            selectable_selector = Select(self.web_driver.driver.find_element_by_class_name('select-strike-price'))
            selectable_selector.select_by_value(value) # select pulldown
        # check
        for i in range(4):
            current_value = self.condition.selector_value
            if value == current_value:
                logging.debug(f"transion_condition: {before_value} to {current_value}")
                return True
            else:
                logging.info(f"transion_condition: error count is {i}")
        raise TransitionFailedError("transion_condition is failed")

    @property
    def condition_info(self) -> ConditionInfo:
        r =  ConditionInfo(trading_name=self.trading_name, timestamp=get_current_time(), round_date=get_today_date(), round_name=self.round.text, condition=self.condition, order_info=self.order_info)
        logging.denug(f"condition_info result: {r}")
        return r

    def round_info(self, round) -> RoundInfo:
        self.transtion_accept_round(round, include_endaccept=True)
        condition_infos = []
        timestamp = get_current_time()
        stock_info = self.stock_price
        for c in self.condition_list.conditions:
            self.transion_condition(c.selector_value)
            condition_infos.append(self.condition)
        r = RoundInfo(trading_name=self.trading_name, timestamp=get_current_time(), round_date=get_today_date(), round_name=self.round.text, condition_infos=condition_infos, stock_price=self.stock_price)
        logging.debug(f"round_info: {r}")
        return r
    
    def all_round_info(self, trading_name) -> AllRoundInfo:
        self.transition_trading(trading_name)
        accept_and_endaccept_round_list = self.accept_and_endaccept_round_list
        result = []
        if len(accept_and_endaccept_round_list) == 1:
            result.append(self.round_info("first"))
        elif len(accept_and_endaccept_round_list) == 2:
            result.append(self.round_info("first"))
            result.append(self.round_info("second"))
        return AllRoundInfo(result)