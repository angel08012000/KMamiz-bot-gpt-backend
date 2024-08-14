from config.config import *
from services.common import *

# 只會回傳文字

def get_schema(endpoint):
    unique_label_name = derivation_unique_label_name(endpoint)
    result = get_schema_text_of_unique_label_name(unique_label_name, endpoint)

    return result

def derivation_unique_label_name(endpoint):
    endpoints = GET_ALL_ENDPOINTS()
    if endpoint in endpoints["endpoint"]:
        index = endpoints["endpoint"].index(endpoint)
        return endpoints["unique_label_name"][index]
    return None

def get_schema_text_of_unique_label_name(name, endpoint):
  data = GET_API(f"/api/v1/data/datatype/{name}")["schemas"][0]

  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The schema of {endpoint} is presented in textual form."
  }))
  res.append(FORMAT_RESPONSE("text", {"tag" : "span", "content" : "Request Schema:"}))
  res.append(FORMAT_RESPONSE("code", {"language" : "typescript", "content" : data["requestSchema"]}))
  res.append(FORMAT_RESPONSE("text", {"tag" : "span", "content" : "Response Schema:"}))
  res.append(FORMAT_RESPONSE("code", {"language" : "typescript", "content" : data["responseSchema"]}))


  return {
    "response" : res
  }

# print(get_schema("(v3) GET /reviews/0"))