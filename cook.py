from dotenv import load_dotenv 
from langchain.llms import OpenAI 
from langchain.chat_models import ChatOpenAI 
from langchain.schema import HumanMessage 
import os 

load_dotenv() 
api_key = os.getenv('OPEN_API_KEY') 
print(api_key) 

llm = OpenAI(temperature=0.9)

chat_model = ChatOpenAI(model_name="gpt-4o", temperature=0) 
ingredients = input() 
messages = [HumanMessage(content=f"{ingredients}を使ったレシピを提案してください")] 
response = chat_model(messages) 
print(response.content)