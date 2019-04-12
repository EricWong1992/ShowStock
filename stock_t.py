# coding:utf8

import threading
import requests
import sys
import time

from Queue import Queue

reload(sys)
sys.setdefaultencoding('utf8')

# 查询的股票id, 上证前缀s_sh, 深证前缀s_sz
stock_nos = {"s_sh600571", "s_sz002415", "s_sh600751", "s_sz002437"}

# 买入提醒价格区间，多个价格按照由低到高排序
stock_buy_price = {
    "s_sh600571": {10.5, 10.7, 11.4},
    "s_sz002415": {33.4},
    "s_sh600751": {3.85},
}
# 卖出提醒价格区间，多个价格按照由高到低排序
stock_sold_price = {
    "s_sh600571": {13.0},
    "s_sz002415": {37.3},
    "s_sh600751": {4.3},
}
# 线程数量
thread_num_default = 3


class Worker(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        while True:
            func, stock_no = self.work_queue.get()
            func(stock_no)
            self.work_queue.task_done()


class Stock(object):
    def __init__(self, code, thread_num):
        self.codes = code
        self.work_queue = Queue()
        self.threads = []
        self.__init_thread_poll(thread_num)

    def __init_thread_poll(self, thread_num):
        for i in range(thread_num):
            self.threads.append(Worker(self.work_queue))

    def __add_work(self, stock_no):
        self.work_queue.put((self.request_info, stock_no))

    def del_params(self):
        for obj in self.codes:
            self.__add_work(obj)
        timer = threading.Timer(2.0, self.del_params)
        timer.start()

    def wait_all_complete(self):
        for thread in self.threads:
            if thread.isAlive():
                thread.join()

    @classmethod
    def request_info(cls, stock_no):
        r = requests.get("http://hq.sinajs.cn/list=%s" % (stock_no,))
        content = r.text[23:-3].split(",")
        # 输出判断
        price_now = float(content[1])
        global last_price
        if price_now != last_price[stock_no]:
            print "-----{} No:{}:{} 价格:{} 涨跌:{} 涨跌幅:{}%-----".format(
                time.strftime("%H:%M:%S", time.localtime(time.time())), stock_no[4:], content[0], content[1], content[2],
                float(content[3])).decode("utf-8").encode("gbk")
            last_price[stock_no] = price_now
        try:
            # 买入判断
            for price in stock_buy_price[stock_no]:
                if price_now <= price:
                    print "---{}  买入->目标:{} 当前:{}---".format(content[0], price, price_now).decode("utf-8").encode(
                        "gbk")
                    break
            # 卖出判断
            for price in stock_sold_price[stock_no]:
                if price_now >= price:
                    print "---{}  卖出->目标:{} 当前:{}---".format(content[0], price, price_now).decode("utf-8").encode(
                        "gbk")
                    break
        except KeyError:
            pass


def main():
    global last_price
    last_price = {}
    for no in stock_nos:
        last_price[no] = 0
    stock = Stock(stock_nos, thread_num_default)
    timer = threading.Timer(2.0, stock.del_params)
    timer.start()

if __name__ == '__main__':
    main()
