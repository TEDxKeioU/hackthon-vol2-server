import os
import asyncio
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()
api_key = os.getenv('OPEN_API_KEY')

async def wait_for_cook_data():
    url = "http://localhost:8000/cook"  # FastAPIのエンドポイント
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(url)
            data = response.json().get("last_cook_data")
            if data:
                return data
            await asyncio.sleep(1)  # 1秒待機して再試行

async def main():
    data = await wait_for_cook_data()
    print("Received data:", data)

    chat_model = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0)
    # ingredients = input("食材を入力してください: ")
    messages = [HumanMessage(content=f"{data}を使ったレシピを提案してください")]
    response = chat_model.invoke(messages)
    print(response.content)

if __name__ == "__main__":
    asyncio.run(main())
