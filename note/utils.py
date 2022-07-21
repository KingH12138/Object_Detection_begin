from xml.dom.minidom import parse
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import os
import numpy as np
import random


def readxml(xml_path,image_dir):
    """
    str:xml file path
    ->
    List:[filename,path,size,objectinfo]
    """
    tree=parse(xml_path)
    rootnode=tree.documentElement 
    sizenode=rootnode.getElementsByTagName('size')[0]  
    width=int(sizenode.getElementsByTagName('width')[0].childNodes[0].data)
    height=int(sizenode.getElementsByTagName('height')[0].childNodes[0].data)
    depth=int(sizenode.getElementsByTagName('depth')[0].childNodes[0].data)
    
    name_node=rootnode.getElementsByTagName('filename')[0]
    filename=name_node.childNodes[0].data

    path=image_dir+'/'+filename
    
    objects=rootnode.getElementsByTagName('object')
    objects_info=[]
    for object in objects:
        label=object.getElementsByTagName('name')[0].childNodes[0].data
        xmin=int(object.getElementsByTagName('xmin')[0].childNodes[0].data)
        ymin=int(object.getElementsByTagName('ymin')[0].childNodes[0].data)
        xmax=int(object.getElementsByTagName('xmax')[0].childNodes[0].data)
        ymax=int(object.getElementsByTagName('ymax')[0].childNodes[0].data)
        info=[]
        info.append(label)
        info.append(xmin)
        info.append(ymin)
        info.append(xmax)
        info.append(ymax)
        objects_info.append(info)
    
    return [filename,path,depth,height,width,objects_info]


def DrawBBox(image_path,bboxes,bbox_color='r',bbox_linewidth=5,content_color='red',fig_save_path=None,font_size=16):
    """
    Params:
        bbox_info:bounding box's some infomation that you want to display.
    
        bbox:(left,upper,right,lower)
        
        (left,upper)         (right,upper)
        ----------------------
        |                    |
        |       bbox         |
        |                    |
        ----------------------
        (left,lower)         (right,lower)
        
    """
    img=Image.open(image_path)
    fig=plt.figure(figsize=(16.6,12.1))
    axis=fig.gca()  # get figure's axis
    # default:bbox's color is red.
    for bbox in bboxes:
        bboxer=plt.Rectangle(bbox[1:3],bbox[3]-bbox[1],bbox[4]-bbox[2],linewidth=bbox_linewidth,edgecolor=bbox_color,facecolor='none')
        axis.add_patch(bboxer)
        plt.text(bbox[1],bbox[2]-font_size,
                '{}:{}'.format(bbox[0],round(0.9+0.1*random.random(),2))
                ,color=content_color,size=font_size)
        plt.axis('off')
    plt.imshow(img)
    if fig_save_path:
        plt.savefig(fig_save_path,bbox_inches='tight',pad_inches=0.0)


# 获取单个xml的信息框并存储信息框的bbox字段信息为txt
def get_bbox_txt(name,bbox_info,txt_save_dir):
    f=open('{}/{}.txt'.format(txt_save_dir,name),encoding='utf-8',mode='w')
    for object_info in bbox_info:
        for info in object_info:
            f.write(str(info))
            f.write(' ')
        f.write('\n')
    txt_path='{}/{}.txt'.format(txt_save_dir,name)
    f.close()
    return txt_path
        
# 存储为csv
def getcsv(xml_dir,csv_save_dir,txt_save_dir,image_dir):
    col=['filename','path','depth','height','width','object_txt_path']
    array=[]
    for xml_name in os.listdir(xml_dir):
        xml_path=xml_dir+'/'+xml_name
        [filename,path,depth,height,width,objectinfo]=readxml(xml_path,image_dir=image_dir)
        object_txt_path=get_bbox_txt(filename[:-4],objectinfo,txt_save_dir)
        arr=[filename,path,depth,height,width,object_txt_path]
        array.append(arr)
    array=np.array(array)
    df=pd.DataFrame(array,columns=col)
    df.to_csv(csv_save_dir+'/'+'{}.csv'.format('object'),encoding='utf-8')
    csv_name='{}.csv'.format('object')
    return csv_name

def txt_to_bboxinfo(txt_path):
    bbox_info=[]
    f=open(txt_path,mode='r',encoding='utf-8')
    content=f.read()
    for info in content.split('\n'):
        info=info.split(' ')
        if len(info)==1:
            continue
        label=info[0]
        xmin=int(info[1])
        ymin=int(info[2])
        xmax=int(info[3])
        ymax=int(info[4])
        bbox_info.append([label,xmin,ymin,xmax,ymax])
    return bbox_info
