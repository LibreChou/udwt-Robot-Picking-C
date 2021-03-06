import os.path as osp
import os
import glob
import imagesize
import json
import cv2
import xml.etree.ElementTree as ET
import numpy as np
import shutil

class Convertor(object):
    def __init__(self, root_dir, output_dir, source='drones', target='coco'):
        self.root_dir = root_dir
        self.output_dir = output_dir
        self.source = source
        self.target = target

        self.splits = ['train_data', 'val_data']
        # self.splits = ['train', 'val', 'test']
        if source == 'drones' and target == 'coco':
            self.start = self.under2coco

    def load_drones(self):
        splits_names = {}
        for split in self.splits:
            img_path = osp.join(self.root_dir, split, 'images')
            image_names = glob.glob(osp.join(img_path, '*.jpg'))
            names = [x.split('\\')[-1].split('.')[0] for x in image_names]
            splits_names[split] = names
        return splits_names



    def under2coco(self):
        splits_names = self.load_drones()
        for split in self.splits:
            coco_json = {
                "info": "",
                "licenses": [],
                "images": [],
                "annotations": [],
                "categories": [

                    {
                        "id": 1,
                        "name": "holothurian",
                        "supercategory": "",
                    },
                    {
                        "id": 2,
                        "name": "echinus",
                        "supercategory": "",
                    },
                    {
                        "id": 3,
                        "name": "scallop",
                        "supercategory": "",
                    },
                    {
                        "id": 4,
                        "name": "starfish",
                        "supercategory": "",
                    }
                ]
            }

            names = splits_names[split]
            img_id = 0
            anno_id = 0
            for name in names:
                # dir = 'F:/dataset/水下目标抓取/under/'+ split + '/images/' + '{}.jpg'.format(name)
                # dir = 'F:/dataset/水下目标抓取/under/'+ split
                # dir = 'F:/dataset/水下目标抓取/' + '{}.jpg'.format(name.replace('\\', '/'))
                # print(dir)
                # width, height = imagesize.get(dir)


                img = cv2.imread(osp.join(self.root_dir, split, 'images', '{}.jpg'.format(name)))

                print(osp.join(self.root_dir, split, 'images', '{}.jpg'.format(name)))
                width, height = img.shape[0], img.shape[1]
                image = {
                    "license": 3,
                    "file_name": "{}.jpg".format(name),
                    "coco_url": "",
                    "height": height,
                    "width": width,
                    "date_captured": "",
                    "flickr_url": "",
                    "id": img_id
                }
                coco_json["images"].append(image)
                if split is not 'test':
                    with open(osp.join(self.root_dir, split, 'annotations', '{}.txt'.format(name)), 'r') as reader:
                        annos = reader.readlines()
                    for anno in annos:
                        anno = anno.strip().split(',')
                        x, y, w, h, score, cls, trc, occ = \
                            int(anno[0]), int(anno[1]), int(anno[2]), int(anno[3]), int(1), int(anno[5]), anno[6], anno[7]
                        annotation = {
                            "id": anno_id,
                            "image_id": img_id,
                            "category_id": cls,
                            "segmentation": [],
                            "area": (w-1)*(h-1),
                            "bbox": [x, y, w-1, h-1],
                            "iscrowd": 0,
                        }
                        coco_json["annotations"].append(annotation)
                        anno_id += 1
                else:
                    annotation = {
                        "id": anno_id,
                        "image_id": img_id,
                        "category_id": 0,
                        "segmentation": [],
                        "area": 0,
                        "bbox": [0, 0, 0, 0],
                        "iscrowd": 0,
                    }
                    coco_json["annotations"].append(annotation)
                    anno_id += 1
                img_id += 1

            with open(osp.join(self.output_dir, '{}.json'.format(split)), 'w') as outfile:
                json.dump(coco_json, outfile)


def xml2txt():
    i = 1
    classall = []
    echinus = 0
    starfish = 0
    scallop = 0
    holothurian = 0
    waterweeds = 0
    for sample in os.listdir('F:/dataset/UNDERALL/2019origin/test_data/annotations/outputs/'):

        xml_file = 'F:/dataset/UNDERALL/2019origin/test_data/annotations/outputs/' + sample
        tree = ET.parse(xml_file)
        root = tree.getroot()
        if root.findall('labeled')[0].text == 'false':
            print(root.findall('labeled')[0].text)
            continue
        # img_name = root.find('frame').text
        txt_file = open('F:/dataset/UNDERALL/2019origin/val_data/annotations/' + sample[:-4] + '.txt', 'w')

        # print(img_name)
        for object in root.find('outputs').find('object').findall('item'):
            cls = object.find('name').text
            # print(cls)
            Xmin = int(object.find('bndbox').find('xmin').text)
            Ymin = int(object.find('bndbox').find('ymin').text)
            Xmax = int(object.find('bndbox').find('xmax').text)
            Ymax = int(object.find('bndbox').find('ymax').text)
            w = Xmax - Xmin
            h = Ymax - Ymin
            if cls == 'echinus' or cls == 'seaurchin':
                cls = int(2)
                echinus += 1
            if cls == 'starfish':
                cls = int(4)
                starfish += 1
            if cls == 'scallop':
                cls = int(3)
                scallop += 1
            if cls == 'holothurian' or cls == 'seacucumber':
                cls = int(1)
                holothurian += 1
            if cls == 'waterweeds':
                continue

            txt_file.write('{},{},{},{},{},{},1,1\n'.format(Xmin, Ymin, w, h, 1, cls))
            # print('cls:{}, Xmin:{}, Ymin:{}, Xmax:{}, Ymax:{}'.format(cls, Xmin, Ymin, Xmax, Ymax))
            if cls not in classall:
                classall.append(cls)
            # a = np.empty([1, 5])
            # b = np.zeros([1, 5])
            # a = np.append(a, b, axis=0)
            # print(a)
            # print(a.shape)
            i += 1


    print(i)
    print(classall)
    print(echinus, starfish, scallop, holothurian, waterweeds)

def splitdata():
    total = os.listdir('F:/dataset/oyster/images/')
    np.random.shuffle(total)
    train_part = total[0:276]
    val_part = total[276:]
    print(len(train_part))
    print(len(val_part))

    i = 0
    print(val_part)
    for val_name in val_part:
        shutil.copy('F:/dataset/oyster/images/' + val_name[:-4] + '.jpg', 'F:/dataset/oyster/val/images/')
        shutil.copy('F:/dataset/oyster/labels/' + val_name[:-4] + '.xml', 'F:/dataset/oyster/val/annotations/')
        i += 1
    print(i)
    for train_name in train_part:
        shutil.copy('F:/dataset/oyster/images/' + train_name[:-4] + '.jpg', 'F:/dataset/oyster/train/images/')
        shutil.copy('F:/dataset/oyster/labels/' + train_name[:-4] + '.xml', 'F:/dataset/oyster/train/annotations/')


def remove_empty_file(path):
    for name in os.listdir(path):
        F=open(path + name)
        if F.readline() == '':
            print(name)
            F.close()
            os.remove(path + name)
            os.remove('F:/dataset/UNDERALL/2019origin/train_data/images/'+name[:-4]+'.jpg')
        # print(name[:-4]+'.txt')



def changeyolov3toRRnet():
    for label in os.listdir('F:/dataset/UNDERALL/mergelabel'):
        F1 = open('F:/dataset/UNDERALL/mergelabel/' + label, 'r')
        F2 = open('F:/dataset/UNDERALL/mergechangetxt/' + label, 'w')
        for line in F1.readlines():
            F2.write('{},{},{},{},{},{},{},{}\n'.format(line.split(' ')[1], line.split(' ')[2], int(line.split(' ')[3]) - int(line.split(' ')[1]), int(line.strip('\n').split(' ')[4]) - int(line.split(' ')[2]), 1, line.split(' ')[0], 0, 0))
            # print('{},{},{},{},{},{},{},{}\n'.format(line.split(' ')[1], line.split(' ')[2], line.split(' ')[3], line.strip('\n').split(' ')[4], 1, line.split(' ')[0], 0, 0))

def change_cls():
    for val_label in os.listdir('F:/dataset/UNDERALL/train_part1/annotations/'):
        F1 = open('F:/dataset/UNDERALL/train_part1/annotations/' + val_label, 'r')
        F2 = open('F:/dataset/UNDERALL/train_part1/annotations_change/' + val_label, 'w')
        for line in F1.readlines():
            if int(line.split(',')[5]) == 1:
                F2.write('{},{},{},{},{},{},{},{}\n'.format(line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], 2, 0, 0))
            if int(line.split(',')[5]) == 3:
                F2.write('{},{},{},{},{},{},{},{}\n'.format(line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], 3, 0, 0))
            if int(line.split(',')[5]) == 4:
                F2.write('{},{},{},{},{},{},{},{}\n'.format(line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], 1, 0, 0))
            if int(line.split(',')[5]) == 2:
                F2.write('{},{},{},{},{},{},{},{}\n'.format(line.split(',')[0], line.split(',')[1], line.split(',')[2], line.split(',')[3], line.split(',')[4], 4, 0, 0))
            else:
                continue


def img2video():
    fps = 15  # 视频帧率
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    videoWriter = cv2.VideoWriter('F:/models/VisDronevideo/video7.avi', fourcc, fps, (2720, 1530))  # (1360,480)为视频大小
    for i in os.listdir('F:/models/VisDronevideo/video7/'):
        img12 = cv2.imread('F:/models/VisDronevideo/video7/' + i)
        #    cv2.imshow('img', img12)
        #    cv2.waitKey(1000/int(fps))
        videoWriter.write(img12)
    videoWriter.release()

def mvfile(path):
    i = 0
    for videoname in os.listdir(path):
        for index in os.listdir(path + videoname):
            for index2 in os.listdir(path + videoname + '/' + index):
                for filename in os.listdir(path + videoname + '/' +index +  '/' +index2):
                    print(path + videoname + '/' + index + '/' +index2 + '/' + filename)
                    shutil.copy(path + videoname + '/' + index + '/' +index2+ '/' + filename,
                                'F:/dataset/UNDERALL/split/annotations/images_2017/' + videoname + '_' + filename)
                    i += 1
    print(i)

def cpimage(path1, path_old, path_new):
    for name in os.listdir(path1):
        shutil.copy(path_old + name[:-4]+ '.jpg', path_new)

def RRtxtresults2matlab(txt_path, out_path):


    label = []
    for txt_name in os.listdir(txt_path):
        id_file = open('F:/dataset/UNDERALL/2019test/test_list.txt')
        # print(txt_name)
        for line in id_file.readlines():
            if line.split(' ')[0] == txt_name[:-4]:
                img_id = line.strip().split(' ')[1]
        # print(img_id)
        id_file.close()
        F = open(txt_path+txt_name, 'r')
        for line in F.readlines():
            matlab_format = [int(img_id), line.split(',')[5], line.split(',')[4], line.split(',')[0], line.split(',')[1],
                             float(line.split(',')[0])+float(line.split(',')[2]), float(line.split(',')[1])+float(line.split(',')[3])]
            label.append(matlab_format)
    np.sort(label, 0)
    matlab = open(out_path+'final.txt', 'w')
    for i in label:
        matlab.write('{} {} {} {} {} {} {}\n'.format(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))


def mmtxtresults2matlab(txt_path, out_path):


    label = []
    for i in range(0, 2901):
        # id_file = open('F:/dataset/UNDERALL/UnderWaterDetection[UPRC2018]/test/test_list.txt')
        # for line in id_file.readlines():
        #     if line.split(' ')[0] == txt_name[:-4]:
        #         img_id = line.strip().split(' ')[1]
        img_id = i + 1
        print(img_id)
        # id_file.close()
        F = open(txt_path+str(i)+'.txt', 'r')
        for line in F.readlines():
            matlab_format = [int(img_id), line.split(',')[5], line.split(',')[4], line.split(',')[0], line.split(',')[1],
                             float(line.split(',')[0])+float(line.split(',')[2]), float(line.split(',')[1])+float(line.split(',')[3])]
            label.append(matlab_format)
    # np.sort(label, 0)
    matlab = open(out_path+'final.txt', 'w')
    for i in label:
        matlab.write('{} {} {} {} {} {} {}\n'.format(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

def split_repeat(new_path, old_path):
    old_name = os.listdir(old_path)
    for new_single_name in os.listdir(new_path):
        if new_single_name not in old_name:
            shutil.copy(new_path + new_single_name, 'F:/dataset/UNDERALL/2018origin/train_2019/annotations/')


def YOLOV3newtxt(path):
    # old_train = open(path + 'train.txt', 'r')
    # new_train =
    return 0


def change2017to2019(path):
    txt2017 = open(path + 'YDXJ0013.txt', 'r')
    for line in txt2017.readlines():
        txt2019 = open('F:/dataset/UNDERALL/split/annotations/2017_txt/'+ 'YDXJ0013_' + line.split(' ')[5] + '.txt', 'a')
        cls = line.strip().split(' ')[9]
        Xmin = int(line.split(' ')[1])
        Ymin = int(line.split(' ')[2])
        Xmax = int(line.split(' ')[3])
        Ymax = int(line.split(' ')[4])
        w = Xmax - Xmin
        h = Ymax - Ymin

        if cls == '"echinus"' or cls == '"seaurchin"':
            cls = int(2)
        if cls == '"starfish"':
            cls = int(4)
        if cls == '"scallop"':
            cls = int(3)
        if cls == '"holothurian"' or cls == '"seacucumber"':
            cls = int(1)
        if cls == '"waterweeds"':
            continue
        txt2019.write('{},{},{},{},{},{},1,1\n'.format(Xmin, Ymin, w, h, 1, cls))


def makegtfinal():
    label = []
    for gtname in os.listdir('F:/dataset/UNDERALL/2019origin/val_data/annotations/'):
        id_file = open('F:/dataset/UNDERALL/2019test/test_list.txt')
        for line in id_file.readlines():
            if line.strip().split(' ')[0] == gtname[:-4]:
                img_id = line.strip().split(' ')[1]
        id_file.close()
        F = open('F:/dataset/UNDERALL/2019origin/val_data/annotations/' + gtname, 'r')
        for line in F.readlines():
            matlab_format = [int(img_id), line.split(',')[5], line.split(',')[4], line.split(',')[0],
                             line.split(',')[1],
                             float(line.split(',')[0]) + float(line.split(',')[2]),
                             float(line.split(',')[1]) + float(line.split(',')[3])]
            label.append(matlab_format)
    # np.sort(label, 0)
    matlab = open('F:/dataset/UNDERALL/txtresults/' + 'gt.txt', 'w')
    for i in label:
        matlab.write('{} {} {} {} {} {} {}\n'.format(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))


if __name__ == '__main__':
    # convert xml to json


    convertor = Convertor('F:/dataset/UNDERALL/2019origin/', 'F:/dataset/UNDERALL/2019coco/annotations/')
    convertor.start()

    # convert xml to txt

    # xml2txt()
    # mvfile('F:/dataset/UNDERALL/split/annotations/2017/')
    # split dataset 0.2/0.8
    # change2017to2019('F:/dataset/UNDERALL/split/annotations/')
    # splitdata()

    # changeyolov3toRRnet()

    # change_cls()

    # remove_empty_file('F:/dataset/UNDERALL/2019origin/train_data/annotations/')
    # mmtxtresults2matlab('F:/dataset/UNDERALL/UnderWaterDetection[UPRC2018]/devkit/txtresults/', 'F:/dataset/UNDERALL/UnderWaterDetection[UPRC2018]/devkit/')

    # split_repeat('F:/dataset/UNDERALL/train_part1/annotations/', 'F:/dataset/UNDERALL/2018origin/new_val/annotations/')
    # cpimage('F:/dataset/UNDERALL/2019origin/val_data/annotations/', 'F:/dataset/UNDERALL/2019origin/test_data/images/', 'F:/dataset/UNDERALL/2019origin/val_data/images/')
    # makegtfinal()
    # RRtxtresults2matlab('F:/dataset/UNDERALL/txtresults/results/', 'F:/dataset/UNDERALL/txtresults/')