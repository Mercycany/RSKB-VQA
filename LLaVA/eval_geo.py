from PIL import Image
import json
import re
from transformers import pipeline
import torch
from transformers import BitsAndBytesConfig
from tqdm import tqdm

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)
model_id = "/mnt/data/models/llava-1.5-7b"
pipe = pipeline("image-to-text", model=model_id, model_kwargs={"quantization_config": quantization_config})



input_json_path = "/home/qiaozijian/LLM_geo/image_QA.json"  
output_json_path = "/home/qiaozijian/LLM_geo/eval_geo_llava_7B.json"  

result = [] 
with open(input_json_path, "r", encoding="utf-8") as f:
    data = json.load(f)
for item in tqdm(data):
    image_path = '/home/qiaozijian/code_factory/LLM_geo/' + item["image"]
    image = Image.open(image_path).convert('RGB')
    QA_list = []
    for item2 in item["Q&A"]:
        question = item2["question"]
        ground_truth = item2["answer"]
        prompt = f"""USER: <image>\nYou are a smart remote sensing image recognition expert. " 
        Please answer my questions based on the pictures. Answers should be concise and accurate.
        If you don't know, you need to answer "sorry, I don't know."
        Next is the question:{question}\nASSISTANT:
        """
        # prompt = f"""You are a smart remote sensing image recognition expert. " 
        # Please answer my questions based on the pictures. Answers should be concise and accurate.
        # If you don't know, you need to answer "sorry, I don't know."
        # Next is the question:{question}.
        # """
        max_new_tokens = 400
        outputs = pipe(image, prompt=prompt, generate_kwargs={"max_new_tokens": 400})
        # print(outputs[0]["generated_text"])
        answer = outputs[0]["generated_text"].split('ASSISTANT:')[-1].strip()
        answer = re.sub(r'\s+', ' ', answer)
        if answer == "":
            answer = "sorry, I don't know."
        print(answer)
        QA_list.append({
                    "question": question,
                    "ground_truth": ground_truth,
                    "answer": answer
                    }
                    )
    result.append({
        "image": item["image"],
        "category": item["category"],
        "address": item["address"],
        "reference": item["reference"],
        "Q&A": QA_list
        })

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)