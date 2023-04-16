""" 
Script to convert xml to to yolo specific annotation. Gotten from:
https://towardsdatascience.com/convert-pascal-voc-xml-to-yolo-for-object-detection-f969811ccba5
"""


import xml.etree.ElementTree as ET
import glob
import os
import json
import shutil

def xml_to_yolo_bbox(bbox, w, h):
    # xmin, ymin, xmax, ymax
    x_center = ((bbox[2] + bbox[0]) / 2) / w
    y_center = ((bbox[3] + bbox[1]) / 2) / h
    width = (bbox[2] - bbox[0]) / w
    height = (bbox[3] - bbox[1]) / h
    return [x_center, y_center, width, height]

def yolo_to_xml_bbox(bbox, w, h):
    # x_center, y_center width heigth
    w_half_len = (bbox[2] * w) / 2
    h_half_len = (bbox[3] * h) / 2
    xmin = int((bbox[0] * w) - w_half_len)
    ymin = int((bbox[1] * h) - h_half_len)
    xmax = int((bbox[0] * w) + w_half_len)
    ymax = int((bbox[1] * h) + h_half_len)
    return [xmin, ymin, xmax, ymax]

classes = []
train_to_test_ratio = 4
input_dir = "annotations/xmls"
output_dir_train = "converted/train/labels/"
output_dir_test = "converted/test/labels/"

image_dir = "images/"
image_dir_train = "converted/train/images/"
image_dir_test = "converted/test/images/"

os.mkdir(output_dir_train)
os.mkdir(output_dir_test)
os.mkdir(image_dir_train)
os.mkdir(image_dir_test)

# GET XML files
count = 0
train_image = True

files = glob.glob(os.path.join(input_dir, '*.xml'))
for fil in files:
    basename = os.path.basename(fil)
    filename = os.path.splitext(basename)[0]
    
    count += 1
    if count == train_to_test_ratio + 1:
        train_image = False
        count = 0
    else:
        train_image = True
    
    result = []
    if not os.path.exists(os.path.join(image_dir, f"{filename}.jpg")):
        print(f"{filename} image does not exist!")
        continue
    else:
        image_file = os.path.join(image_dir, f"{filename}.jpg")
        if (train_image):
            shutil.copy(image_file, image_dir_train)
        else:
            shutil.copy(image_file, image_dir_test)


    tree = ET.parse(fil)
    root = tree.getroot()
    width = int(root.find("size").find("width").text)
    height = int(root.find("size").find("height").text)

    for obj in root.findall('object'):
        label = obj.find("name").text
        if label not in classes:
            classes.append(label)
        index = classes.index(label)
        pil_bbox = [int(x.text) for x in obj.find("bndbox")]
        yolo_bbox = xml_to_yolo_bbox(pil_bbox, width, height)
        bbox_string = " ".join([str(x) for x in yolo_bbox])
        result.append(f"{index} {bbox_string}")

    if result:
        if (train_image):
            with open(os.path.join(output_dir_train, f"{filename}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(result))
        else:
            with open(os.path.join(output_dir_test, f"{filename}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(result))

with open('classes.txt', 'w', encoding='utf8') as f:
    f.write(json.dumps(classes))