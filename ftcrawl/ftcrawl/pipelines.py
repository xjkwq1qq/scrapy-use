# -*- coding: utf-8 -*-
import scrapy
import uuid
import pymongo
import time
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#Ftcrawl的对象存储
class FtcrawlPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.urls_seen = {}
        self.mongo_uri = mongo_uri
        self.collection_name = 'alumn_home'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri='localhost:27017',
            mongo_db='fcenter'
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.client.fcenter.authenticate("fcenter", "123456")
        self.db = self.client.fcenter

    def process_item(self, item, spider):
        if item['type'] == 'ftcrawl':
            del item['type']
            item['createtime'] = int(time.time()*1000)
            if item['url'] in self.urls_seen:
                item['sourceId'] = self.urls_seen[item['url']]
                self.db[self.collection_name].insert_one(dict(item))
            else:
                item['_id'] = str(uuid.uuid1())
                self.db[self.collection_name].insert_one(dict(item))
                self.urls_seen[item['url']] = item['_id']
        else:
            return item

    def close_spider(self, spider):
        self.client.close()

    if __name__ == "__main__":
        mongo_uri = '127.0.0.1:27017'
        connection = pymongo.MongoClient(mongo_uri)
        connection.fcenter.authenticate("fcenter", "123456")
        db = connection.fcenter

        a = {'a': 'b', '_id': '1'}
        #db['alumn_home'].insert_one(a)
        print int(time.time() * 1000)

#抓取列表图片数据处理
class FtimagePipeline(ImagesPipeline):
    min_width = 0
    min_height = 0
    def __init__(self, store_uri, download_func=None, settings=None):
        super(ImagesPipeline, self).__init__(store_uri, settings=settings, download_func=download_func)
        self.client = pymongo.MongoClient('localhost:27017')
        self.client.fcenter.authenticate("fcenter", "123456")
        self.collection_name = 'alumn_home'
        self.db = self.client.fcenter
        self.thumbs = {}

    def process_item(self, item, spider):
        if item:
            if item['type'] == 'ftimage':
                return super(ImagesPipeline, self).process_item(item, spider)
            else:
                return item


    def get_media_requests(self, item, info):
        if item:
            if item['type'] == 'ftimage':
                yield scrapy.Request(item['image'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]

        if not image_paths:
            raise DropItem("Item contains no images")

        self.db[self.collection_name].update({'image': item['image']}, {'$set': {'img': image_paths[0]}}, multi=True)

        #def close_spider(self, spider):
        #    self.client.close()

    def file_path(self, request, response=None, info=None):
        path = super(ImagesPipeline, self).file_path(request, response, info)
        return 'root/'+time.strftime('%Y%m%d%H', time.localtime(time.time()))+'/'+path

#子对象抓取
class FtchildPipeline(ImagesPipeline):
    min_width = 0
    min_height = 0

    def __init__(self, store_uri, download_func=None, settings=None):
        super(ImagesPipeline, self).__init__(store_uri, settings=settings, download_func=download_func)
        self.client = pymongo.MongoClient('localhost:27017')
        self.client.fcenter.authenticate("fcenter", "123456")
        self.collection_name = 'alumn_child'
        self.db = self.client.fcenter
        self.thumbs = {}

    def get_media_requests(self, item, info):
        if item:
            if item['type'] == 'ftchild':
                yield scrapy.Request(item['picurl'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['img'] = image_paths[0]
            self.db[self.collection_name].update({'_id': item['_id']}, {'$set': {'img': image_paths[0]}})

    def file_path(self, request, response=None, info=None):
        path = super(FtchildPipeline, self).file_path(request, response, info)
        return 'child/'+time.strftime('%Y%m%d%H', time.localtime(time.time()))+'/'+path


