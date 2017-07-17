# -*- coding:utf-8 -*-
import scrapy
import pymongo
import uuid

class FtchildSpider(scrapy.Spider):
    name = "ftchild"
    start_urls = []
    def __init__(self):
        client = pymongo.MongoClient('localhost:27017')
        client.fcenter.authenticate("fcenter", "123456")
        self.db = client.fcenter
        self.collection_name = 'alumn_child'
        for item in self.db['alumn_home'].find({'style': {'$in': ['xiandai']}, 'sourceId': {'$exists': False}, 'complate': {'$exists': False}}, {'url': 1}):
            sourceId = None
            for source in self.db['alumn_home'].find({'url': item['url'], 'complate': {'$exists': True}}, {"_id": 1}):
                sourceId = source['_id']
            if sourceId:
                self.db['alumn_home'].update({'_id': item['_id']}, {'$set': {'sourceId': sourceId}}, multi=True)
            else:
                print item['url']
                self.start_urls.append(item['url'])
        #self.start_urls.append('http://home.fang.com/album/p22120532_1_203_11/')

    def parse(self, response):
        type = 'ftchild'
        datas = response.css('script').re('var jsonsearch=\[\{.*?\}\]\;')

        pid = ''
        for item in self.db['alumn_home'].find({'url': response.url, 'sourceId': {'$exists': False}}, {'_id': 1}):
            pid = item['_id']
            break

        if len(datas) == 0:
            self.db['alumn_home'].update({'_id': pid}, {'$set': {'complate': 1}})
            return

        formatdatas = datas[0].replace('var jsonsearch=', '')[:-1].replace('\"', '\\\"').replace('\'', '\"')


        try:
            dataparse = self.parse_js(formatdatas)
            self.db['alumn_home'].update({'_id': pid}, {'$set': {'complate': 1}})
            for item in dataparse:
                dbitem = {
                    '_id': str(uuid.uuid1()),
                    'pid': pid,
                    'type': type,
                    'title': item['title'],
                    'picurl': item['picurl'],
                    'des': item['des'],
                }
                imgExist = list(self.db[self.collection_name].find({'picurl': dbitem['picurl'], 'img': {'$exists': True}}, {'img': 1}))
                if imgExist.__len__() > 0:
                    dbitem['img'] = imgExist[0]['img']
                    self.db[self.collection_name].insert_one(dict(dbitem))
                else:
                    self.db[self.collection_name].insert_one(dict(dbitem))
                    yield dbitem
        except Exception as err:
            print '删除id相关:'+str(pid)
            self.db[self.collection_name].remove({'_id': pid})
            self.db[self.collection_name].remove({'sourceId': pid})
            self.db['alumn_child'].remove({'pid': pid})
            return

    def parse_js(self, expr):
        """
        解析非标准JSON的Javascript字符串，等同于json.loads(JSON str)
        :param expr:非标准JSON的Javascript字符串
        :return:Python字典
        """
        obj = eval(expr, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        return obj



    if __name__ == "__main__":
        client = pymongo.MongoClient('localhost:27017')
        client.fcenter.authenticate("fcenter", "123456")
        db = client.fcenter
        collection_name = 'alumn_home'
        count = 0
        for item in db['alumn_home'].find({'sourceId': {'$exists': False}, 'img': {'$exists': False}}, {'_id': 1}):
            db['alumn_home'].remove({'sourceId': item['_id']})
            db['alumn_home'].remove({'_id': item['_id']})
        #print db['alumn_home'].find({'sourceId':{'$exists':False},'img':{'$exists':False}}, {'_id': 1}).count()
        #     count = db['alumn_home'].find({'_id': item['sourceId']}).count()
        #     if count == 0:
        #         print item['sourceId']

       # print db['alumn_child'].find({'img':{'$exists':False}}).count()