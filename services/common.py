from config.config import *
import requests
import sys
import json
import yaml
import urllib.parse
from PIL import Image
from base64 import encodebytes
import io
import json
from jsonschema import validate

def GET_PROMPTS(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def GET_YAML(file_path):
    with open(file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

def GET_API(suffix):
  r = requests.get(f"{PREFIX}{suffix}")

  if r.status_code!=requests.codes.ok:
      sys.exit(f"{r.status_code} Failed to call API")

  # r.text 可以拿到回覆的內容，型態為 str
  response = json.loads(r.text) # str to json
  
  return response

def GET_ALL_ENDPOINTS():
  endpoint = []
  unique_label_name = []

  res = GET_API("/api/v1/data/label")

  for r in res:
    label = r[1]
    service, namespace, version, method, path = r[0].split('\t')
    temp = f"{service}\t{namespace}\t{version}\t{method}\t{label}"

    endpoint.append(f"({version}) {method} {label}")
    unique_label_name.append(urllib.parse.quote(temp, safe=""))

  return {"endpoint": endpoint, "unique_label_name": unique_label_name}

def GET_ALL_SERVICES():
  res = GET_API("/api/v1/data/label")
  services = []

  for r in res:
    service, namespace, version, method, path = r[0].split('\t')
    services.append(f"{service}.{namespace}.{version}")
    
  # 暴力處理順序不同的問題 START
  services[0], services[1], services[2], services[3], services[4], services[5] = services[2], services[5], services[3], services[0], services[1], services[4]
  # END

  return {"service": services}

def GET_IMAGE_BASE64(image_path):
  pil_img = Image.open(image_path, mode='r') # reads the PIL image
  byte_arr = io.BytesIO()
  pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
  encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
  return encoded_img

def FORMAT_RESPONSE(key, value):
  with open('./config/schema/example.json', 'r') as file:
    json_data = file.read()

  res = json.loads(json_data)
  res["ui_type"] = key
  res["data"][key] = value

  return res

def VALIDATE_RESPONSE(response):
  # 讀取 JSON Schema
  with open('./config/schema/schema.json', 'r') as schema_file:
    schema = json.load(schema_file)

  try:
    validate(instance=response, schema=schema)
    return response
  except Exception as e:
    print(f"API response 未通過驗證，錯誤訊息：{e}")