from config.config import *
from services.common import *
from services.screenshot import *

# 會回傳文字、照片、連結
def get_insight(insight, service, mode):
  insight = insight.replace(' ', '_')
  data = call_function_by_name(f"get_{insight}_data")
  result = call_function_by_name(f"get_{mode}", insight, service, data)
  
  return result or None

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


# data 的形式為
# {"<<service_name>>" : {"SIUC", <<value>>, ...}, ...}
def get_cohesion_data():
  suffix = f"/api/v1/graph/cohesion/{NAMESPACE}"
  response = GET_API(suffix)
  # print(response)

  cohesion = {
    "service": [],
    "SIDC": [],
    "SIUC": [],
    "TSIC": [],
  }

  for data in response:
    cohesion["service"].append(data["uniqueServiceName"].replace('\t', '.'))
    cohesion["SIDC"].append(data["dataCohesion"])
    cohesion["SIUC"].append(data["usageCohesion"])
    cohesion["TSIC"].append(data["totalInterfaceCohesion"])
  
  return cohesion

def get_coupling_data():
  suffix = f"/api/v1/graph/coupling/{NAMESPACE}"
  response = GET_API(suffix)

  coupling = {
    "service": [],
    "AIS": [],
    "ADS": [],
    "ACS": [],
  }

  for data in response:
    coupling["service"].append(data["uniqueServiceName"].replace('\t', '.'))
    coupling["AIS"].append(data["ais"])
    coupling["ADS"].append(data["ads"])
    coupling["ACS"].append(data["acs"])
    
  return coupling

def get_instability_data():
    suffix = f"/api/v1/graph/instability/{NAMESPACE}"
    response = GET_API(suffix)

    instability = {
      "service": [],
      "FanOut": [],
      "FanIn": [],
      "SDP": [],
    }

    for data in response:
      instability["service"].append(data["uniqueServiceName"].replace('\t', '.'))
      instability["FanOut"].append(data["dependingOn"])
      instability["FanIn"].append(data["dependingBy"])
      instability["SDP"].append(data["instability"])
    
    return instability

def get_all_insights_data():
  return {
    "cohesion" : get_cohesion_data(),
    "coupling" : get_coupling_data(),
    "instability" : get_instability_data()
  }



def get_text(insight, service, data):
  # 為何仍用 if-else，是因為表格行列要放的屬性不同，無法共用程式碼
  keys = list(data.keys())
  tbody = []

  if insight != "all_insights":
    tbody.append([""] + keys[1:])

    for s in data[keys[0]]:
      index = data['service'].index(s)
      tbody.append([s, data[keys[1]][index], data[keys[2]][index], data[keys[3]][index]])

    res = []
    res.append(FORMAT_RESPONSE("text", {
      "tag" : "span",
      "content" : f"The {insight} of {service} is presented in textual form."
    }))

    res.append(FORMAT_RESPONSE("table", {
      "thead" : insight,
      "tbody" : tbody
    }))

    return {
      "response": res
    }
  
  else:
    index = data[keys[0]]['service'].index(service)
    index_now = 1
    
    tbody.append(['colspan' if i%2==0 else item for i, item in enumerate(keys * 2)])

    for insight_name in keys:
      sub_keys = list(data[insight_name].keys())[1:] #SIDC, SIUC, TSIC

      for sub_key in sub_keys:
        value = data[insight_name][sub_key][index]
        index_now = (index_now-1) % 3 + 1
        try:
          tbody[index_now] += [sub_key, value]
        except IndexError:
          # 如果索引超出範圍，就直接加入新資料
          tbody.append([sub_key, value])
        index_now += 1
    
    res = []
    res.append(FORMAT_RESPONSE("text", {
      "tag" : "span",
      "content" : f"The {insight} of {service} are presented in textual form."
    }))

    res.append(FORMAT_RESPONSE("table", {
      "thead" : service,
      "tbody" : tbody
    }))

    return {
      "response" : res
    }

def set_image_param(service):
  with open('./config/kmamiz/insight.json', 'r') as file:
    json_data = file.read()

  param = json.loads(json_data)
  param['URL_or_HTML'] = f"{PREFIX}/insights"

  if service!=None:
    services = GET_ALL_SERVICES()["service"]
    num = len(services)
    target = services.index(service)
    for p in param['IMAGES_PARAM']:
      p['SUM'] = str(num)
      p['TARGET'] = str(target)

  with open('./config/kmamiz/insight.json', 'w') as json_file:
    json.dump(param, json_file)

def get_image(insight, service, data):
  set_image_param(service)

  h = Highlighted("insight", False if service=="all_service" else True)
  h.screenshot_with_highlighted()

  image_name = ["cohesion.png", "coupling.png", "instability.png"] if insight=="all_insights" else [f"{insight}.png"]
  
  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The {insight} of {service} {'are' if insight=='all_insights' else 'is'} presented in image form."
  }))
  for name in image_name:
    # res.append(FORMAT_RESPONSE("text", {"tag" : "span", "content" : name.split(".")[0]}))
    res.append(FORMAT_RESPONSE("image", {"base64" : GET_IMAGE_BASE64(f"{IMAGE_PATH}/{name}")}))
  
  return {
    "response": res
  }

def get_url(insight, service, data):
  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The {insight} of {service} is presented in URL form."
  }))
  res.append(FORMAT_RESPONSE("link", {
    "url" : f"{PREFIX}/insights",
    "content" : insight.capitalize()
  }))
  
  return {
    "response" : res
  }
