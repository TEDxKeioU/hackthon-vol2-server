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
        await client.delete(RECIPE_API_URL) # レシピを削除、そうじゃないと前回の物が出てしまう
        while True:
            response = await client.get(url)
            data = response.json().get("last_cook_data")
            if data:
                return data
            await asyncio.sleep(1)  # 1秒待機して再試行

async def main():
    data = await wait_for_cook_data()
    print("Received data:", "cook.py", data)

    ingredients = data.get("ingredients", [])
    avoid = data.get("ingredients", {}).get("avoid", [])
    want = data.get("ingredients", {}).get("want", [])
    cooking_time = data.get("cookingTime")
    temp = data.get("temp")

    messages = [
        HumanMessage(
            content=(
                f"{','.join(want)}を使い、{','.join(avoid)}を使わない料理レシピを、対話形式を避け、提案してください。"
                f"以下の情報も考慮してください。\n"
                f"【入れたい食材】: {want}\n"
                f"【避けたい食材】: {','.join(avoid)}\n"
                f"【調理時間】: {cooking_time}\n"
                f"【気温】: {temp}℃"
            )
        )
    ]

    print(messages)
    chat_model = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini", temperature=0)
    response = chat_model.invoke(messages)
    recipe = response.content
    print("Generated recipe:", recipe)

    # FastAPIにレシピを送信
    async with httpx.AsyncClient() as client:
        await client.post(RECIPE_API_URL, json={"recipe": recipe})

if __name__ == "__main__":
    asyncio.run(main())
