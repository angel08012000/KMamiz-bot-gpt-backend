from config.config import *
from services.common import *

def get_message_history(user_id):
  print(f"{user_id} 想來拿歷史紀錄")
  return ""

def greeting(user_id):
  res = []
  res.append(FORMAT_RESPONSE("text", {
      "tag" : "span",
      "content" : "Hi! I’m KMamiz-Bot! Please select one of the below feature types according to the information you need. You can also type your query directly."
    }))
  res.append(FORMAT_RESPONSE("button", {"name": "function", "value": "Service Metrics"}))
  res.append(FORMAT_RESPONSE("button", {"name": "function", "value": "Dependency Insights"}))
  res.append(FORMAT_RESPONSE("button", {"name": "function", "value": "Swagger UI"}))
  res.append(FORMAT_RESPONSE("button", {"name": "function", "value": "Dependency Insights"}))
  MESSAGE_HISTORY[user_id] = [{
    "from": SYSTEM,
    "text": res
  }]