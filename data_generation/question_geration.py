import requests
import json
import os
from tqdm import tqdm 
import openai
import re


# openai.api_key = 'sk-b1f8fa6eb5144513b1bc5a6b2d1c5f0a' # 你的 Forward Key
# openai.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"

openai.api_key = 'fk228775-E4JCNFU0V72II07ToNX7vEFkwa1l1irv' # 你的 Forward Key
openai.api_base = "https://oa.api2d.net"
# ##筛选已删除的图片
# def del_json(input_json):
#     new_json = []
#     delete_list = []
#     with open (input_json, 'r') as f:
#         data = json.load(f)
#         for item in tqdm(data):
#             image_path = item["image"]
#             if os.path.exists(image_path):
#                 new_json.append(item)
#             else:
#                 delete_list.append(image_path)
#     ##保存json文件
#     with open("out_data.json", 'w') as f:
#         json.dump(new_json, f)
#     with open("del_data.json", 'w') as f:
#         json.dump(delete_list, f)    
# del_json("/home/qiaozijian/code_factory/data.json")


def prompt_template(address,category):

    prompt = f"""I will provide you with a {category} remote sensing image of the location at '{address}'. Your tasks are as follows:
1. Retrieve the relevant reference information from Wikipedia about the location '{address}', but do not include any links in your response.
2. Generate 3 questions and their corresponding answers based on the Wikipedia content. Ensure the questions are not too difficult, and the answers are concise and straightforward.
3.Do not appear "{address}" in the question, replace it with 'the image'
4. Format your response as JSON in the following structure.  :{{"reference": "Wikipedia content", "Q&A": [{{"question": "Question 1", "answer": "Answer 1"}}, {{"question": "Question 2", "answer": "Answer 2"}}, {{"question": "Question 3", "answer": "Answer 3"}}]}}.
"""
    return prompt


def get_json(text):
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        print(json_str)
        try:
            json_data = json.loads(json_str)

            reference = json_data["reference"]
            qa_list = json_data["Q&A"]
            print(reference)
            print(qa_list)
            print("JSON数据已成功提取")
            return reference, qa_list
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            reference = "load fail"
            qa_list = [ ]
            return reference, qa_list
    else:
        print("未找到有效的JSON内容。")

with open("/home/qiaozijian/code_factory/out_data.json", 'r') as f:
    data =  json.load(f)
    ##取前10个data中的数据
    new_data = []
    data = data[0:150]
    for item in tqdm(data):
        # try:
        image_address = item["address"]
        image_category = item["category"]
        prompt = prompt_template(image_address,image_category)
        print(prompt)
        response = openai.ChatCompletion.create(            
            model="gpt-4o",  
            # model="qwen-turbo",  
            messages=[
                {"role": "system", "content": "You are a geography expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        output_text = response.choices[0].message.get("content", '')
        print(output_text)
        reference , qa_list = get_json(output_text)
        new_data.append({
            "image":item["image"],
            "category":item["category"],
            "address":item["address"],
            "reference":reference,
            "Q&A":qa_list
        })
        # except Exception as e:
        #     print(f"Error processing item {image_address}: {e}")
        #     continue


    ##保存new——data
    with open("image_QA_1501.json", 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=4)








