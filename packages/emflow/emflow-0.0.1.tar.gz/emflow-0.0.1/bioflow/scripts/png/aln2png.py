#!/usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import re

import numpy as np
import mrcfile
from functools import reduce
from scipy import ndimage
from PIL import Image,ImageDraw

parser = argparse.ArgumentParser(description='convert mrc to png')
parser.add_argument('filePath', type=str, help='the file path of origin img')
args = parser.parse_args()

#读取数据
res={}
module=''
index=0
with open(args.filePath,'r') as f:
    for line in f:
        if(line.startswith(' ')):
            line = line.strip()
            if(line==''): continue
            arr=re.split('\s+',line)
            if(module=='setting'):
                res[module][arr[0].strip(':')]=arr
            elif(module=='globalShift'):
                if(arr[0]!='stackID'):
                    res[module][arr[0]]=arr
            else:
                if(arr[0]=='patchID:'):
                    index=int(arr[1])
                    res[module][index]={}
                elif(arr[0]!='Converge:'):
                    res[module][index][arr[0]]=arr
        else:
            module=line.strip()
            res[module]={}
#图片大小
nX=int(res['setting']['stackSize'][1])
nY=int(res['setting']['stackSize'][2])
#行列数
gridX=int(res['setting']['patches'][1])
gridY=int(res['setting']['patches'][2])
#行高与列宽
gridXL=nX/gridX
gridYL=nY/gridY
#创建图片
img = Image.new("RGB",(nX,nY),"white")
draw = ImageDraw.Draw(img)
#cell
for row in range(gridX+1):
    draw.line([(row*gridXL,0),(row*gridXL,nY)],fill=(205,205,205),width=4)
for col in range(gridY+1):
    draw.line([(0,col*gridYL),(nX,col*gridYL)],fill=(205,205,205),width=4)
#center
cX=nX/2
cY=nY/2
draw.line([(cX+float(v[1]),cY+float(v[2])) for v in res['globalShift'].values()],fill=(255,0,0),width=2)
#patches
for vv in res['localShift'].values():
    draw.line([(float(v[1])+float(v[3]),float(v[2])+float(v[4])) for v in vv.values()],fill=(0,0,255),width=2)

img.save(args.filePath+".png")

#save globalShift
