import os
import asyncio
import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

load_dotenv()
api_key = os.getenv('OPEN_API_KEY')

RECIPE_API_URL = "http://localhost:8000/recipe"

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

    ingredients = ",".join(data.get("ingredients", []))
    avoid = ",".join(data.get("avoid", []))
    want = ",".join(data.get("want", []))
    cooking_time = data.get("cookingTime")
    temp = data.get("temp")

    messages = [
        HumanMessage(
            content=(
                f"{ingredients}を使ったレシピを,対話形式を避け、簡潔に提案してください。ただし、以下の情報も考慮して。"
                f"【食材】: {ingredients}\n"
                f"【避けたい食材】: {avoid}\n"
                f"【入れたい食材】: {want}\n"
                f"【調理時間】: {cooking_time}\n"
                f"【気温】: {temp}℃"
            )
        )
    ]

    chat_model = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0)
    response = chat_model.invoke(messages)
    recipe = response.content
    print("Generated recipe:", recipe)

    # FastAPIにレシピを送信
    async with httpx.AsyncClient() as client:
        await client.post(RECIPE_API_URL, json={"recipe": recipe})

if __name__ == "__main__":
    asyncio.run(main())
