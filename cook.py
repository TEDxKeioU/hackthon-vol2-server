from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI 
from langchain.schema import HumanMessage 
import os 

load_dotenv() 
api_key = os.getenv('OPEN_API_KEY')

# llm = OpenAI(openai_api_key=api_key, temperature=0.9)

chat_model = ChatOpenAI(openai_api_key=api_key, model_name="gpt-4o", temperature=0) 
ingredients = input() 
messages = [HumanMessage(content=f"{ingredients}を使ったレシピを提案してください")] 
response = chat_model.invoke(messages)
print(response.content)