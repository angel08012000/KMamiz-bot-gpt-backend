from services.common import *

def send_to_gpt(system, user):
  messages = []
  messages.append(format_mes("system", system))
  messages.append(format_mes("user", user))

  return messages

def format_mes(role, content):
  return {"role": role, "content": content}

def to_classify_intent_entity():
  content = ''
  content += GET_PROMPTS('./config/prompts/intent_classification_and_entity_extraction.txt')
  
  content = content.replace('<INTENT_ENTITY_MAPPING>', str(GET_YAML('./config/capability/intent_entity_mapping.yml')))
  content = content.replace('<AVAILABLE_ENTITY_VALUE>', str(GET_YAML('./config/capability/available_entity_value.yml')))

  return content

def to_request_missing_entities(inform):
  # 讓 GPT 問問句
  ask_for = "Here is the content of the sentence, please help me rephrase it."

  if len(inform['missing'])!=0:
    ask_for += f"You should provide the value of {inform['missing']}."
  
  if len(inform['wrong'])!=0:
    ask_for += f"The value of {inform['wrong']} is/are wrong."

  return ask_for

def to_request_entities_use_button(inform):
  print(f"缺少的資料: {inform}")
  available_entity = GET_YAML('./config/capability/available_entity_value.yml')
  res = []

  def create_response(entity, message):
    res.append(FORMAT_RESPONSE("text", {"tag": "span", "content": message}))
    for button in available_entity[entity]:
      res.append(FORMAT_RESPONSE("button", {"name": entity, "value": button}))

  # Handling 'wrong'
  if inform['wrong']:
    for entity in inform['wrong']:
      create_response(entity, f"The value of the {entity} can only be one of the following (please select).")

  # Handling 'missing'
  if inform['missing']:
    for entity in inform['missing']:
      create_response(entity, f"You need to provide the value of the {entity} (please select).")

  res.append(FORMAT_RESPONSE("text", {"tag": "span", "content": "After making your selection, please press 'Submit'."}))

  return {
    "response" : res
  }

def to_request_intent():
  ask_for = "Here is the content of the sentence, please help me rephrase it."
  ask_for += "I don't know what do you want to search!"

  return ask_for
