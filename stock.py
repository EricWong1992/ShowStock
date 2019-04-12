# coding:utf8

import threading
import requests
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

# 查询的股票id, 上证前缀s_sh, 深证前缀s_sz
stock_no = {"s_sh600571", "s_sz002415", "s_sh600751", "s_sh600839"}

# 买入提醒价格区间，多个价格按照由低到高排序
stock_buy_price = {
    "s_sh600571": {10.5, 10.7, 11.73},
    "s_sz002415": {33.4},
    "s_sh600751": {3.85},
}
# 卖出提醒价格区间，多个价格按照由高到低排序
stock_sold_price = {
    "s_sh600571": {13.0},
    "s_sz002415": {37.3},
    "s_sh600751": {4.3},
}


def request_info():
    for no in stock_no:
        r = requests.get("http://hq.sinajs.cn/list=%s" % (no,))
        content = r.text[23:-3].split(",")
        # 输出判断
        price_now = float(content[1])
        global last_price
        if price_now != last_price[no]:
            print "-----{} No:{}:{} 价格:{} 涨跌:{} 涨跌幅:{}%-----".format(time.strftime("%H:%M:%S", time.localtime(time.time())), no[4:], content[0], content[1], content[2], float(content[3])).decode("utf-8").encode("gbk")
            last_price[no] = price_now
        try:
            # 买入判断
            for price in stock_buy_price[no]:
                if price_now <= price:
                    print "---{}  买入->{}---".format(content[0], price).decode("utf-8").encode("gbk")
                    break
            # 卖出判断
            for price in stock_sold_price[no]:
                if price_now >= price:
                    print "---{}  卖出->{}---".format(content[0], price).decode("utf-8").encode("gbk")
                    break
        except KeyError:
            pass
    global timer
    timer = threading.Timer(2.0, request_info)
    timer.start()


def main():
    global last_price
    last_price = {}
    for no in stock_no:
        last_price[no] = 0
    timer = threading.Timer(2.0, request_info)
    timer.start()


if __name__ == '__main__':
    main()
