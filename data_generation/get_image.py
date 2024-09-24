import requests
import os
import csv
import json

API_KEY = ''
# 输出文件夹
output_folder = 'images'
os.makedirs(output_folder, exist_ok=True)
Num=1
New_json = []

def get_latlng_from_address(address): ##输入地址，返回坐标
  get_latlng_url= "https://maps.googleapis.com/maps/api/geocode/json"
  params = {
    'address': address,
    'key': API_KEY
  }
  response = requests.get(get_latlng_url, params=params)
  latitude = None
  longitude = None
  if response.status_code == 200:
       data = response.json()
       if data['status'] == 'OK':
           results = data['results']
           if results:
               location = results[0]['geometry']['location']
               latitude = location['lat']
               longitude = location['lng']
           else:
               print("No results found.")
       else:
           print(f"Geocoding failed with status: {data['status']}")
  else:
       print(f"Request failed with status code: {response.status_code}")
  return latitude, longitude


def get_image_from_adress(address): ##输入地址，返回图像
  latitude, longitude = get_latlng_from_address(address)
  get_image_url = "https://maps.googleapis.com/maps/api/staticmap?"
  params = {
    "center": f"{latitude},{longitude}",
    "zoom": 17,
    "size": "800x800",
    "maptype": "satellite",
    "key": API_KEY
  }
  response = requests.get(get_image_url, params=params, timeout=(5, 10))
  return response

def get_image_from_csv(inputfile_path):
  global Num
  with open(inputfile_path, 'r') as file:
    csv_reader = csv.DictReader(file)  # 使用DictReader读取文件
    for row in csv_reader:
      try:
        Num += 1
        category = row['Category'].replace(' ', '_')
        address = row.get('Attraction Name', '') + row.get('Location', '')
        Response = get_image_from_adress(address)
        if Response is not None and Response.status_code == 200:
          ##保存图片
          category_path = os.path.join(output_folder, category)
          os.makedirs(category_path, exist_ok=True)
          image_filename = os.path.join(category_path, f"{category}_000{Num}.png")
          print(image_filename)
          with open(image_filename, 'wb') as image_file:
            image_file.write(Response.content)
            print(image_filename)
          New_json.append({
                  "image": image_filename,
                  "category": category,
                  "address": address})
        else:
          print(f"Request failed with status code: {Response.status_code}")
      except Exception as e:  # 捕获所有异常
        print(f"Error processing row: {row}, Error: {e}")  # 打印错误信息，以便调试
    ##保存json
    with open('data.json', 'w') as json_file:
      json.dump(New_json, json_file)

get_image_from_csv('us_attractions_categorized.csv')
