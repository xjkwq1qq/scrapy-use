# -*- coding:utf-8 -*-
import random
import threading
import urllib2

#代理池对象
class proxyPool():
    proxys = {}
    counter_lock = threading.RLock()


    #获取代理ip
    def getproxy(self):

        if self.proxys.__len__() < 5:
            self.getproxy_daxiang()
        proxy = random.choice(self.proxys.keys())
        self.useproxy(proxy)
        return proxy

    #使用代理
    def useproxy(self, proxy):
        count = self.proxys[proxy]
        if count is None:
            return

        if count <= 1:
            del self.proxys[proxy]
        else:
            self.proxys[proxy] = count-1


    #从大象代理中获取代理
    def getproxy_daxiang(self):
        print '#########重新获取代理###########'
        self.counter_lock.acquire()
        if self.proxys.__len__() < 5:
            response = urllib2.urlopen('http://vtp.daxiangdaili.com/ip/?tid=557969394506479&num=5000');
            datas = response.read()
            for data in datas.split('\r\n'):
                self.proxys[data] = 3
        self.counter_lock.release()

    #代理数量
    def proxysize(self):
        print self.proxys.__len__()

proxy_pool = proxyPool()

if __name__ == "__main__":
    ip = proxy_pool.getproxy()
    print ip
    proxy_pool.proxysize()
    print proxy_pool.getproxy()
    print proxy_pool.getproxy()
    proxy_pool.proxysize()
