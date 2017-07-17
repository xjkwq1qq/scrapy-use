# -*- coding:utf-8 -*-
import scrapy
import urlparse
import pymongo

class FtcrawlSpider(scrapy.Spider):
    name = "ftcrawl"
    start_urls = []

    def __init__(self):
        a1s = ['keting','chufang','woshi','weishengjian','xuanguan','canting','yangtai','ertongfang','yimaojian','shufang']
        #a2s = ['xiandai','jianou','jianyue','zhongshi','oushi','tianyuan','dizhonghai','hunda','meishi','rihan','dongnanya','gudian']
        a2s = ['jianyue']
        a3s = ['beijqiang','piaochuang','zoulang','diaoding','louti','chugui','yigui','chuang','dianshigui','shafa','chuanglian','geduan','zuhegui','chuwugui','shugui','batai','xiegui','chaji','tatami','zhaopianqiang','bizhi','pingfeng','yingerchuang','dengju','canzhuo','yugang','chuangtougui','jiugui','shuzhuangtai','shujia']
        #a1s = ['keting']
        #a2s = ['xiandai']
        #a3s = ['beijqiang']
        for a1 in a1s:
            for a2 in a2s:
                for a3 in a3s:
                    self.start_urls.append('http://home.fang.com/album/lanmu/?a1='+a1+'&a2='+a2+'&a3='+a3+'&page=1&sortid=11')

    def parse(self, response):
        # follow links to author pages
        start = 1
        end = 2
        for href in response.xpath('//*[@id="zxxgtlist_B07_01"]/ul/i[2]/a/@href').extract():
            url = response.urljoin(href)
            params = urlparse.parse_qs(urlparse.urlparse(url).query, True)
            end = int(params['page'][0])+1
        for i in range(start, end):
            yield response.follow(response.url.replace('page=1', 'page='+str(i)), self.parsehome)

    def parsehome(self, response):
        params = urlparse.parse_qs(urlparse.urlparse(response.url).query, True)
        features = params['a1'][0]
        style = params['a2'][0]
        part = params['a3'][0]
        #print response.css('.photo_list>ul>li').__len__()
        for content in response.css('.photo_list>ul>li'):
            yield {
                'type': 'ftcrawl',
                'features': features,
                'style': style,
                'part': part,
                'url': content.css('ol>span>a::attr(href)').extract_first(),
                'title': content.css('ol>p>a::attr(title)').extract_first(),
                'image': content.css('ol>span>a>img::attr(src)').extract_first()
            }

    if __name__ == "__main__":
        client = pymongo.MongoClient('localhost:27017')
        client.fcenter.authenticate("fcenter", "123456")
        db = client.fcenter

