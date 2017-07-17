# -*- coding:utf-8 -*-
import scrapy
import pymongo
import uuid

class FtchildSpider(scrapy.Spider):
    name = "ftchild_params"
    start_urls = []

    def __init__(self, category=None, *args, **kwargs):
        super(scrapy.Spider, self).__init__(*args, **kwargs)
        client = pymongo.MongoClient('localhost:27017')
        client.fcenter.authenticate("fcenter", "123456")
        self.db = client.fcenter
        self.collection_name = 'alumn_child'
        print '抓取风格：'+category
        if category:
            for item in self.db['alumn_home'].find({'style': {'$in': [category]}, 'sourceId': {'$exists': False}, 'complate': {'$exists': False}}, {'url': 1}):
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
        collection_name = 'ftchild'
        count = 0
        rt = db.alumn_child.remove({'img': {'$exists': False}})
        print rt

        #print count
        #data = '[{picid:25470151,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/66/8/pic/007413342000/1000x1500.jpg",title:"田园风格三居室卧室衣柜装修效果图大全",name:"",FavariteNum:0,des:"在材料选择上多倾向于较硬、光挺、华丽的材质。餐厅基本上都与厨房相连,厨房的面积较大,操作方便、功能强大。",type:1,cutdes:""},{picid:25470152,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/79/71/pic/007739850200/1000x1500.jpg",title:"田园风格三居室餐厅酒柜装修效果图欣赏",name:"",FavariteNum:0,des:"田园风格之所以称为田园风格,是因为田园风格表现的主题以贴近自然,展现朴实生活的气息。田园风格最大的特点就是:朴实,亲切,实在。",type:1,cutdes:""},{picid:25470153,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/86/34/pic/007740159700/1000x1500.jpg",title:"田园风格三居室餐厅酒柜装修效果图欣赏",name:"",FavariteNum:0,des:"田园风格的朴实是众多选择此风格装修者最青睐的一个特点,因为在喧哗的城市中,人们真的很想亲近自然,追求朴实的生活,于是田园生活就应运而生啦!喜欢田园风格的人大部分都是低调的人,懂得生活,懂得生活来之不易!",type:1,cutdes:""},{picid:25470154,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/29/60/pic/007740483000/1000x1500.jpg",title:"田园风格三居室卧室电视柜装修效果图大全",name:"",FavariteNum:0,des:"起居室一般较客厅空间低矮平和,选材上也多取舒适、柔性、温馨的材质组合,可以有效地建立起一种温情暖意的家庭氛围,电视等娱乐用品也放在这一空间中,可以想象在电视广告的声色、锅碗瓢盆的和乐、孩子嬉戏的杂音下,这"三区一体"的其乐融融。",type:1,cutdes:"起居室一般较客厅空间低矮平和,选材上也多取舒适、柔性、温馨的材质组合,可以有效地建立起一种温情暖意的家庭氛围,电视等娱乐..."},{picid:25468896,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/58/18/pic/007466640700/1000x1500.jpg",title:"现代简约四居室客厅背景墙装修效果图大全",name:"",FavariteNum:0,des:"客厅作为入门的第一视觉中心,一定要体现整个居所的格调,灰色的墙漆立刻有温暖的感觉迎面而来。",type:1,cutdes:""},{picid:25468897,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/98/92/pic/007466737000/1000x1500.jpg",title:"现代简约四居室卧室背景墙装修效果图大全",name:"",FavariteNum:0,des:"此卧室注重的是安静、祥和,都市的忙碌生活,早已让我们烦腻了花天酒地,灯红酒绿,我们更喜欢的一个安静,祥和,看上去明朗宽敞舒适的家,来消除工作的疲惫。",type:1,cutdes:""},{picid:25468898,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/49/33/pic/007466845100/1000x1500.jpg",title:"现代简约四居室卧室背景墙装修效果图欣赏",name:"",FavariteNum:0,des:"卧室的设计维持一贯的时尚、舒适的基调,并建立了实用贴心的收纳功能,精品专柜般品味。",type:1,cutdes:""},{picid:25468895,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/89/22/pic/007466542700/1000x1500.jpg",title:"现代简约四居室客厅背景墙装修效果图",name:"",FavariteNum:0,des:"客厅以家具的造型简约舒适,布局对称雅致,使整体空间大气并附有内涵,在装饰细节上崇尚美好居家情调,使之具有家的真实内容和居住的舒适与惬意,最终赋予它一种氛围、一种品位、一个真正意义上的家园。",type:1,cutdes:""},{picid:25468510,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/74/48/pic/007311273800/1000x1500.jpg",title:"现代简约三居室客厅背景墙装修效果图",name:"",FavariteNum:0,des:"亮点营造典雅、和谐、舒适、高贵的气质。电视墙的造型既简单又有品味,符合整体装修风格。使整个风格浪漫又温馨.",type:1,cutdes:""},{picid:25468511,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/19/54/pic/007311380400/1000x1500.jpg",title:"现代简约三居室客厅背景墙装修效果图欣赏",name:"",FavariteNum:0,des:"融入了现代生活元素,体现出豪华大气,惬意和浪漫。",type:1,cutdes:""},{picid:25468512,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/95/17/pic/007311475300/1000x1500.jpg",title:"现代简约三居室餐厅餐桌装修效果图欣赏",name:"",FavariteNum:0,des:"淡雅的色彩柔和的光线,华贵的线脚加上精致餐具,营造了浪漫的气氛。",type:1,cutdes:""},{picid:25468513,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/36/96/pic/007311579700/1000x1500.jpg",title:"现代简约三居室厨房橱柜装修图片",name:"",FavariteNum:0,des:"简约风格已经大行其道几年了,仍然保持很猛的势头,这是因为人们装修时总希望在经济、实用、舒适的同时,体现一定的文化品味",type:1,cutdes:""},{picid:25468394,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/12/61/pic/007253360400/1000x1500.jpg",title:"简欧风格三居室客厅背景墙装修效果图",name:"",FavariteNum:0,des:"本案的中设计从简单到繁杂、从整体到局部,精雕细琢,给人一丝不苟的印象。一方面保留了材质、色彩的大致风格,让人感受到传统的历史痕迹与浑厚的文化底蕴,同时又摒弃了过于复杂的肌理和装饰,简化了线条。",type:1,cutdes:""},{picid:25468395,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/60/72/pic/007253440300/1000x1500.jpg",title:"简欧风格三居室卧室背景墙装修效果图",name:"",FavariteNum:0,des:"卧室主要以床头背景墙为主,以金茶与软包相结合,体现温馨提高亮度,使得整个空间更加温馨舒适。实用的飘窗可以让主人在闲暇之余多了一个娱乐休闲之地。",type:1,cutdes:""},{picid:25468396,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/32/50/pic/007253542200/1000x1500.jpg",title:"简欧风格三居室卫生间瓷砖装修图片",name:"",FavariteNum:0,des:"卫生间实景效果图",type:1,cutdes:""},{picid:25468393,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/91/59/pic/007253245100/1000x1500.jpg",title:"简欧风格三居室客厅背景墙装修图片",name:"",FavariteNum:0,des:"本案在注重装饰效果的同时,用现代的手法和材质还原古典气质,具备了古典与现代的双重审美效果,完美的结合也让人们在享受物质文明的同时得到了精神上的慰藉。",type:1,cutdes:""},{picid:25468276,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/40/42/pic/007226467600/1000x1500.jpg",title:"中式古典三居室客厅背景墙装修效果图",name:"",FavariteNum:0,des:"本案在形式上以浪漫主义为基础,运用大理石和华丽多彩的织物,以及精美和多姿曲线的家具,让室内显示出豪华、富丽的特点,充满强烈的动感效果。",type:1,cutdes:""},{picid:25468277,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/27/67/pic/007226546100/1000x1500.jpg",title:"中式古典三居室餐厅餐桌装修效果图欣赏",name:"",FavariteNum:0,des:"变形的直线与曲线相互作用以及猫叫家具与装饰工艺手段的运用,构成室内华美厚重的气氛。",type:1,cutdes:""},{picid:25468278,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/54/90/pic/007226345700/1000x1500.jpg",title:"中式古典三居室卧室背景墙装修效果图欣赏",name:"",FavariteNum:0,des:"画框的线条部位装饰为线条或金边,在造型设计上既要突出凹感,又要有优美的弧线,并期望这种表现能够完整地体现客户主球品质,典雅生活,视生活为艺术的人生态度。",type:1,cutdes:""},{picid:25468279,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/66/91/pic/007226245600/1000x1500.jpg",title:"中式古典三居室卧室背景墙装修效果图欣赏",name:"",FavariteNum:0,des:"在繁杂多变的世界里,现代人已是烦扰不休,而简单、自然的生活空间却能让人身心舒畅,感到宁静和安逸",type:1,cutdes:""},{picid:25468265,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/63/8/pic/007156020200/1000x1500.jpg",title:"混搭风格四居室餐厅灯具装修效果图欣赏",name:"",FavariteNum:0,des:"混搭风格糅合东西方美学精华元素,将古今文化内涵完美地结合于一体,充分利用空间形式与材料,创造出个性化的家居环境。",type:1,cutdes:""},{picid:25468266,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/94/94/pic/007157052700/1000x1500.jpg",title:"混搭风格四居室儿童房书柜装修效果图欣赏",name:"",FavariteNum:0,des:"混搭得是否成功,关键看是否和谐。最简单的方法是确定家具的主风格,用配饰、家纺等来搭配",type:1,cutdes:""},{picid:25468267,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/1/60/pic/007162263800/1000x1500.jpg",title:"混搭风格四居室书房灯具装修图片",name:"",FavariteNum:0,des:"中西元素的混搭是主流,其次还有现代与传统的混搭。",type:1,cutdes:""},{picid:25468268,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/91/7/pic/007162870400/1000x1500.jpg",title:"混搭风格四居室卫生间浴缸装修图片",name:"",FavariteNum:0,des:"在同一个空间里,不管是“传统与现代”,还是“中西合璧”,都要以一种风格为主,靠局部的设计增添空间的层次。",type:1,cutdes:""},{picid:25468269,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/35/24/pic/007163752000/1000x1500.jpg",title:"混搭风格四居室卫生间灯具装修图片",name:"",FavariteNum:0,des:"混搭是现在家居装修中一种新型的装修理念,比如如有的人喜欢简约风格,与此同时,他又非常喜欢地中海风格,他就可以在家居的设计之中将简约以及地中海两者相结合来对家进行装修设计。",type:1,cutdes:""},{picid:25468270,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/99/49/pic/007164301300/1000x1500.jpg",title:"混搭风格四居室卫生间灯具装修效果图大全",name:"",FavariteNum:0,des:"自己喜欢的一切融入装修之中,就产生了混搭这一概念,混搭不仅仅是一种装修,更是一种实现实现个性化装修的手段,它适用于任何风格,别样的混搭设计,展现出了家居的百变风情",type:1,cutdes:""},{picid:25468271,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/55/93/pic/007165025500/1000x1500.jpg",title:"混搭风格四居室卧室床装修效果图大全",name:"",FavariteNum:0,des:"主调不明-家里的装修所呈现出的风格要统一,不能太过于复杂和繁琐,一般来说,超过三种以上的风格调和在一起,对整体和谐是一大挑战,更何况一些风格本身就是不相容的。",type:1,cutdes:""},{picid:25468272,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/75/54/pic/007165569200/1000x1500.jpg",title:"混搭风格四居室卧室床装修效果图大全",name:"",FavariteNum:0,des:"色彩太多-混搭在色彩的选择上要小心,免得整体显乱,在考虑整体风格的时候就需要定下一两个基本色,然后在这个基础上添加同色系的家具,配饰则可以选择柔和的对比色以提升亮度,也可以选择中间色以显示内敛。",type:1,cutdes:""},{picid:25468273,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/26/86/pic/007167066300/1000x1500.jpg",title:"混搭风格四居室卧室床头柜装修图片",name:"",FavariteNum:0,des:"风格混搭这种折中而个性的气质塑造并不是可以随意、简单的进行组合,它是建立在一定的文化修养上的。",type:1,cutdes:""},{picid:25468264,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/91/34/pic/007159468500/1000x1500.jpg",title:"混搭风格四居室客厅电视柜装修效果图欣赏",name:"",FavariteNum:0,des:"混搭并不是简单地把各种风格的元素放在一起做加法,而是把它们有主有次地组合在一起。",type:1,cutdes:""},{picid:25467890,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/32/92/pic/006573574700/1000x1500.jpg",title:"现代简约二居室客厅沙发装修效果图欣赏",name:"",FavariteNum:0,des:"白墙的不经意涂抹修整的结果也形成一种特殊的不规则表面。",type:1,cutdes:""}]'
        #data = '[{picid:25470154,picurl:"http://img1n.soufunimg.com/viewimage/zxb/2016_08/20/29/60/pic/007740483000/1000x1500.jpg",title:"田园风格三居室卧室电视柜装修效果图大全",name:"",FavariteNum:0,des:"起居室一般较客厅空间低矮平和,选材上也多取舒适、柔性、温馨的材质组合,可以有效地建立起一种温情暖意的家庭氛围,电视等娱乐用品也放在这一空间中,可以想象在电视广告的声色、锅碗瓢盆的和乐、孩子嬉戏的杂音下,这"三区一体"的其乐融融。",type:1,cutdes:"起居室一般较客厅空间低矮平和,选材上也多取舒适、柔性、温馨的材质组合,可以有效地建立起一种温情暖意的家庭氛围,电视等娱乐..."}]'
        #data = '[{test:\'""asdadad\'}]'.replace('\"', '\\\"').replace('\'', '\"')
        #print data
        #obj = eval(data, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        #print obj