import tqdm from tqdm
import os
import csv
import json



##筛选已删除的图片
def del_json(input_json):
    new_json = []
    delete_list = []
    with open (input_json, 'r') as f:
        data = json.load(f)
        for item in tqdm(data):
            image_path = item["image"]
            if os.path.exists(image_path):
                new_json.append(item)
            else:
                delete_list.append(image_path)
    ##保存json文件
    with open("out_data.json", 'w') as f:
        json.dump(new_json, f)
    with open("del_data.json", 'w') as f:
        json.dump(delete_list, f)    
del_json("data.json")