#!/usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import numpy as np
import mrcfile
from functools import reduce
from scipy import ndimage
from PIL import Image


### functions ###

def readMrc(filePath):
    data=[]
    with mrcfile.open(filePath, permissive=True) as mrc:
        shape=mrc.data.shape
        shape_len=len(shape)
        if(shape_len==3 and shape[0]>1):
            data=reduce(lambda x,y:x+y,mrc.data)
            data/=shape[0]
        elif(shape_len==3):
            data=mrc.data[0]
        else:
            data=mrc.data
    return data

def readStar(filePath):
    star=[]
    with open(args.starFilePath,'r') as f:
        header=[]
        header_len=0
        module='data_'
        mod_step='header'
        for line in f:
            line=line.strip()
            if(module=='data_' and line=='loop_'):
                module='loop_'
            elif(module=='loop_'):
                if(mod_step=='header'):
                    if(line.startswith('_rln',0,4)):
                        header.append(line.split()[0][4:])
                    else:
                        mod_step='data'
                        header_len=len(header)
                if(mod_step=='data'):
                    star.append(dict(zip(header,line.split()[0:header_len])))
    return star

def data2img(rawData):
    data=ndimage.gaussian_filter(rawData,1)
    dmax=np.max(data)
    dmin=np.min(data)
    data=(data-dmin)*255/(dmax-dmin)
    img=Image.fromarray(data).convert('L')
    return img

def image_compose(IMAGES,IMAGE_COLUMN,IMAGE_ROW,IMAGE_SIZE,IMAGE_SAVE_PATH):
    to_image = Image.new('L', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))
    for i in range(len(IMAGES)):
        img=IMAGES[i]
        x=i%IMAGE_COLUMN
        y=int(i/IMAGE_COLUMN)
        img.resize((IMAGE_SIZE, IMAGE_SIZE),Image.ANTIALIAS)
        to_image.paste(img, (x * IMAGE_SIZE, y * IMAGE_SIZE))
    return to_image.save(IMAGE_SAVE_PATH)


### tasks ###

def mrc2png(filePath):
    data2img(readMrc(filePath)).save(filePath+".png")

def extractPick(mrcFilePath,starFilePath,size=100):
    image_mrc=data2img(readMrc(mrcFilePath))
    star=readStar(starFilePath)
    star.sort(reverse=True,key=lambda x:float(x['AutopickFigureOfMerit']))
    w=int(size/2)
    imgs=[]
    for cell in star[0:9]:
        x=int(float(cell['CoordinateX']))
        y=int(float(cell['CoordinateY']))
        img=image_mrc.crop((x-w,y-w,x+w+1,y+w+1))
        imgs.append(img)
    image_compose(imgs,3,3,size+1,args.starFilePath+".png")

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='extract picks from mrc')
    parser.add_argument('mrcFilePath', type=str, help='the file path of motion corrected mrc')#,nargs='?',default='/media/zhangtaotao/软件/work/xinyue/test/MotionCor/May08_03.05.02.bin.mrc'
    parser.add_argument('starFilePath', type=str, help='the file path of star file')#,nargs='?',default='/media/zhangtaotao/软件/work/xinyue/test/Pick/May08_03.05.02.bin.star'
    args = parser.parse_args()

    extractPick(args.mrcFilePath,args.starFilePath)


