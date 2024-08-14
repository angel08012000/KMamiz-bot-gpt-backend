import json
import copy
from config.config import *
from services.common import *
from services.gpt.generator import *

def validate_intent(res, user_id):
    data_dict = eval(res.choices[0].message.content)
    print(f"----- 判斷出的資料: {data_dict} -----")

    # content = '{"get_insight":{"service":"ratings.book.v1", "mode":"123"}}'

    intent = list(data_dict.keys())[0]

    # 確認最近一次得到的 intent，並拿到 entity
    if intent == "no_intent":
        if len(HISTORY[user_id]["INTENTS"])==0:
          return {}
        intent = HISTORY[user_id]["INTENTS"][0]
        entity = data_dict.get("no_intent", "")
        print(f'>>>>> 本輪沒有 intent，上次的為: {HISTORY[user_id]["INTENTS"][0]}')
    elif intent == "out_of_scope":
       return {}
    else:
        HISTORY[user_id]["INTENTS"].insert(0, intent)
        entity = data_dict.get(intent, "")

    # 檢查 entity 是否皆已獲得
    inform = validate_entity(intent, entity, user_id)
    print(f"----- 收集之所有資料: {HISTORY} -----")

    return {"execution": intent} if not (inform["missing"] or inform["wrong"]) else inform
    
def validate_entity(intent, exist_entities, user_id):
  # 檢查 value 是否正確
  wrong = []
  available_entity = GET_YAML('./config/capability/available_entity_value.yml')

  for entity_name, entity_value in exist_entities.copy().items():
    if entity_value not in available_entity.get(entity_name, []):
      wrong.append(entity_name)
      exist_entities.pop(entity_name)

  # 加入 HISTORY(新的值會覆蓋舊的)
  HISTORY[user_id]["ENTITIES"].update(exist_entities)

  # 檢查缺少的
  intent_entity = GET_YAML('./config/capability/intent_entity_mapping.yml')
  needed = set(intent_entity.get(intent, []))
  if intent == "get_insight" and "insight" in HISTORY[user_id]["ENTITIES"] and HISTORY[user_id]["ENTITIES"]["insight"] == "all insights":
    # 移除特定的元素
    needed.discard("service")
  missing = needed.difference(HISTORY[user_id]["ENTITIES"])
  missing = missing.difference(wrong) # 也要扣掉錯的

  # missing: 缺少的, wrong: value 不合法的
  return {"missing": list(missing), "wrong": wrong}
