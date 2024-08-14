from config.config import *
from services.common import *
import services.kmamiz.swagger as  swagger
import services.kmamiz.schema as schema
import services.kmamiz.insight as insight
import services.kmamiz.dependency as dependency
import services.gpt.connection as  connection
import services.gpt.generator as generator
import services.history.message as message

### 呼叫對應功能 START ###
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

def get_insight(user_id):
  return insight.get_insight(HISTORY[user_id]["ENTITIES"]["insight"], HISTORY[user_id]["ENTITIES"].get("service", None) , HISTORY[user_id]["ENTITIES"]["mode"])

def get_dependency_graph(user_id):
  return dependency.get_dependency(HISTORY[user_id]["ENTITIES"]["graph"], HISTORY[user_id]["ENTITIES"]["mode"])

def get_swagger(user_id):
  return swagger.get_swagger(HISTORY[user_id]["ENTITIES"]["service"])

def get_schema(user_id):
  return schema.get_schema(HISTORY[user_id]["ENTITIES"]["endpoint"])

### 呼叫對應功能 END ###

def deal_history(who, data, user_id):
  MESSAGE_HISTORY[user_id].append({
    "from": who,
    "text": data
  })


from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
  
@app.route('/api/user', methods=['GET'])
def get_user_id():
  global USERID
  temp = USERID
  HISTORY[temp] = {"INTENTS": [], "ENTITIES": {}}
  message.greeting(temp)
  USERID = str(eval(USERID)+1)

  return {"user_id": temp}

@app.route('/api/history', methods=['POST'])
def get_user_history():
  try:
    data = request.get_json()
    return {"res": MESSAGE_HISTORY[data['id']]}
  except Exception as e:
    return jsonify({'error': str(e)})

@app.route('/api/message', methods=['POST'])
def connect_to_web():
  try:
    data = request.get_json()
    
    temp = []
    temp.append(FORMAT_RESPONSE("text", {
      "tag" : "span",
      "content" : data['user']
    }))
    deal_history("user", temp, data['id'])
    mes = generator.send_to_gpt(generator.to_classify_intent_entity(), data['user'])
    result = connection.connect_validate(mes, data['id'])

    if "execution" not in result:
      # 生成問句再傳給 gpt START
      if "missing" in result or "wrong" in result:
        #content = generator.to_request_missing_entities(result)
        res_to_front_web = generator.to_request_entities_use_button(result)
        deal_history("system", res_to_front_web["response"], data['id'])
        return res_to_front_web
      else:
        content = generator.to_request_intent()
        result = connection.connect_return([generator.format_mes("system", content)])
        res_to_front_web = [FORMAT_RESPONSE("text", {"tag": "span", "content": result})]
        deal_history("system", res_to_front_web, data['id'])
        return {
          "response" : res_to_front_web
        }
      # 生成問句再傳給 gpt END
    
    else:
      # 執行對應功能
      response = call_function_by_name(result["execution"], data['id'])
      deal_history("system", response["response"], data['id'])

      return response
  
  except Exception as e:
    return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)