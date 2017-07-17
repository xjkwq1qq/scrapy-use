# -*- coding:utf-8 -*-
from PIL import Image
import os
import os.path
img_water = 'e:/logo.jpg'

def watermark(img_source):
    try:
        im = Image.open(img_source)
        mark = Image.open(img_water)
        layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
        layer.paste(mark, (im.size[0]-200, im.size[1]-60))
        out = Image.composite(layer, im, layer)
        im.close()
        out.save(img_source)
        out.close()
    except Exception as e:
        print(">>>>>>>>>>> WaterMark EXCEPTION:  " + str(e))
        return False
    else:
        return True

def waterdir(rootdir):
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            watermark(os.path.join(parent, filename))


if __name__ == "__main__":
    #watermark("e:/f3bb148191b13f54772282b277f5dffd56e61130.jpg", )
    date = '20170717'
    for i in range(8, 9):
        if i < 10:
            waterdir('E:\\fang\\child\\'+date+'0'+str(i))
        else:
            #print 'E:\\fang\\child\\'+date+str(i)
            waterdir('E:\\fang\\child\\'+date+str(i))
    #waterdir("E:\\fang\\child")