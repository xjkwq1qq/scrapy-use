# -*- coding:utf-8 -*-
import scrapy
import pymongo

class FtimageSpider(scrapy.Spider):
    name = "ftimage"
    start_urls = []
    image_urls = scrapy.Field()

    def __init__(self):
        self.start_urls.append('http://cq.fang.com/')
        #self.start_urls.append('https://www.baidu.com')
        client = pymongo.MongoClient('localhost:27017')
        client.fcenter.authenticate("fcenter", "123456")
        self.db = client.fcenter
        self.collection_name = 'alumn_home'

    def parse(self, response):
        type = 'ftimage'
        print 'start ftimage'

        for item in self.db[self.collection_name].find({'sourceId': {'$exists': False}, 'img': {'$exists': False}}, {'image': 1, "_id": 1}):
            img = None
            for source in self.db['alumn_home'].find({'image': item['image'], 'img': {'$exists': True}}, {"img": 1}):
                img = source['img']
            if img:
                self.db['alumn_home'].update({'_id': item['_id']}, {'$set': {'img': img}}, multi=True)
            else:
                item['type'] = type
                yield item
            #count += 1
            #print count
        #return {'image': 'http://img1n.soufunimg.com/viewimage/jiancai/business/xgt/201408/21/957/8caf070d7efdf6ca87c43a7557c75da3/432x324c.jpg', '_id':u'e1fc3ecf-622b-11e7-816d-005056c00008', 'type': 'ftimage'}



