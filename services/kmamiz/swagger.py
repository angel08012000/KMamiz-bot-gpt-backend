from config.config import *
from services.common import *

# 只會回傳連結

def get_swagger(service):
  service_encoded = service.replace(".", ENCODE_CHAR)

  res = []
  res.append(FORMAT_RESPONSE("text", {
    "tag" : "span",
    "content" : f"The swagger of {service} is presented in textual form."
  }))

  res.append(FORMAT_RESPONSE("link", {
    "url" : f"{PREFIX}/swagger/{service_encoded}",
    "content" : service
  }))

  return {
    "response": res
  }

# print(get_swagger("details.book.v1"))