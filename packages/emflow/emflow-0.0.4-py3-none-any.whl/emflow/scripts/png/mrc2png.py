#!/usr/bin/python3
# -*- coding:utf-8 -*-

import argparse
import numpy as np
import mrcfile
from functools import reduce
from scipy import ndimage
from PIL import Image

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


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='convert mrc to png')
    parser.add_argument('filePath', type=str, help='the file path of origin img')
    args = parser.parse_args()

    data=ndimage.gaussian_filter(readMrc(args.filePath),1)

    dmax=np.max(data)
    dmin=np.min(data)
    data=(data-dmin)*255/(dmax-dmin)

    im = Image.fromarray(data).convert('L')
    im.save(args.filePath+".png")
