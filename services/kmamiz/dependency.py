from config.config import *
from services.common import *
from services.screenshot import *

# 會回傳文字(直接、間接圖)、照片、連結
'''
- service dependency graph
- endpoint dependency graph
- direct service dependencies
- indirect service dependencies
'''
def get_dependency(dependency, mode):
  result = call_function_by_name(f"get_{mode}", dependency)
  
  return result

def call_function_by_name(function_name, *args, **kwargs):
  global_symbols = globals()

  # 檢查 function 是否存在＆可用
  if function_name in global_symbols and callable(global_symbols[function_name]):
    # 呼叫
    function_to_call = global_symbols[function_name]
    return function_to_call(*args, **kwargs)
  else:
    # 丟出錯誤
    raise ValueError(f"Function '{function_name}' not found or not callable.")

# direct service dependencies
# indirect service dependencies
def get_text(dependency):
  print("有近來！！！！！！")
  if dependency.split(' ')[1]!="service":
    res = FORMAT_RESPONSE("text", {
      "tag" : "span",
      "content" : "The dependency would be clearer with an image or URL."
    })

    return {
      "response" : [res]
    }
  
  suffix = f"/api/v1/graph/chord/{dependency.split(' ')[0]}/{NAMESPACE}"
  response = GET_API(suffix)
  print(f"dependency 圖表的 response: ")
  print(response)
  data = response["links"]

  formatted_data = {}

  for d in data:
    service_from = d["from"]
    formatted_data.setdefault(service_from, f"service {service_from} depends on\n\n")
    val = d['value']
    formatted_data[service_from] += f"{d['to']} {val} {'time' if val <= 1 else 'times'}\n"

  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The {dependency} is presented in textual form."
  }))

  for value in formatted_data.values():
    res.append(FORMAT_RESPONSE("text", {"tag": "span", "content": value}))

  print("回覆:")
  print(res)

  return {
    "response": res
  }

# All
def set_image_param(dependency):
  json_name = "service_dependencies" if dependency.split(" ")[1] == "service" else dependency.replace(" ", "_")

  with open(f'./config/kmamiz/{json_name}.json', 'r') as file:
    json_data = file.read()

  param = json.loads(json_data)
  param['URL_or_HTML'] = f"{PREFIX}/insights" if dependency.split(" ")[1] == "service" else PREFIX
  
  with open(f'./config/kmamiz/{json_name}.json', 'w') as json_file:
    json.dump(param, json_file)

def get_image(dependency):
  set_image_param(dependency)
  json_name = "service_dependencies" if dependency.split(" ")[1] == "service" else dependency.replace(" ", "_")

  h = Highlighted(json_name, False)
  h.screenshot_with_highlighted()

  image_name = [f"{dependency.replace(' ', '_')}.png"]

  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The {dependency} is presented in image form."
  }))
  for name in image_name:
    # res.append(FORMAT_RESPONSE("text", {"tag": "span", "content": name.split(".")[0]}))
    res.append(FORMAT_RESPONSE("image", {"base64": GET_IMAGE_BASE64(f"{IMAGE_PATH}/{name}")}))

  return {
    "response": res
  }

# All
def get_url(dependency):
  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The {dependency} is presented in URL form."
  }))
  res.append(FORMAT_RESPONSE("link", {
    "url" : f"{PREFIX}/{'insights' if dependency.split(' ')[1]=='service' else ''}",
    "content" : dependency
  }))

  return {
    "response": res
  }
