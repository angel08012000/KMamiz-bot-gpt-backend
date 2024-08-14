from openai import OpenAI
import services.gpt.generator as  generator
import services.gpt.validator as  validator

client = OpenAI()

def connect_validate(mes, user_id):
  # mes = [{"role": role, "content": content}, ...]
  response = client.chat.completions.create(model="gpt-3.5-turbo", messages= mes)
  return validator.validate_intent(response, user_id)

def connect_return(mes):
  response = client.chat.completions.create(model="gpt-3.5-turbo", messages= mes)
  return response.choices[0].message.content