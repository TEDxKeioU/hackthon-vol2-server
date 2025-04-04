from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess, sys

from fastapi.responses import JSONResponse

from schemas import PostTodo
from models import TodoModel
from settings import SessionLocal

from sqlalchemy.orm import Session

# global変数の初期化
last_cook_data = None #cookのための変数の初期化
last_recipe = None #recipeの初期化

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 許可するオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],  # 許可するHTTPメソッドを指定
    allow_headers=["*"],  # 許可するHTTPヘッダーを指定
)

### >>>>> Hello API >>>>> ###
@app.get("/")
async def root():
    return {"message": "Hello World"}
### <<<<< Hello API <<<<< ###

### >>>>> Recipe API >>>>> ###
@app.post("/recipe")
def save_recipe(recipe: dict = Body(...)):
    global last_recipe
    last_recipe = recipe.get("recipe")
    print("Saved Recipe:", last_recipe)
    return {"messsage": "Recipe saved successfully"}

@app.get("/recipe")
def get_recipe():
    headers = {"Cache-Control": "no-cache"}
    return JSONResponse(content={"recipe": last_recipe}, headers=headers)

@app.delete("/recipe")
def delete_recipe():
    global last_recipe
    last_recipe = None
### <<<<< Recipe API <<<<< ###

### >>>>> Todo API >>>>> ###
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# データベースからToDo一覧を取得するAPI
@app.get("/todo")
def get_todo(
        db: Session = Depends(get_db)
    ):
    # query関数でmodels.pyで定義したモデルを指定し、.all()関数ですべてのレコードを取得
    return db.query(TodoModel).all()

# ToDoを作成するAPI
@app.post("/todo")
def post_todo(
        todo: PostTodo, 
        db: Session = Depends(get_db)
    ):
    # 受け取ったtitleからモデルを作成
    db_model = TodoModel(title = todo.title)
    # データベースに登録（インサート）
    db.add(db_model)
    # 変更内容を確定
    db.commit()
    return {"message": "success"}

# ToDoを削除するAPI
@app.delete("/todo/{id}")
def delete_todo(
        id: int,
        db: Session = Depends(get_db)
    ):
    delete_todo = db.query(TodoModel).filter(TodoModel.id==id).one()
    db.delete(delete_todo)
    db.commit()

    return {"message": "success"}
def create_todo(todo_obj: PostTodo, db):
    db_model = TodoModel(title=todo_obj.title)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model
### <<<<< Todo API <<<<< ###

### >>>>>> Cook API >>>>> ###
# ingredientsを受け取るAPI
@app.post("/cook")
def post_cook_info(info: dict = Body(...)):
    global last_cook_data
    last_cook_data = info
    print("Received data:", last_cook_data, "end")

    subprocess.run([sys.executable, "cook.py"], check=True)
    return {"status": "success", "data": last_cook_data }

@app.get("/cook")
def get_last_cook_data():
    print("get_last_cook_data")
    return {"status": "success", "last_cook_data": last_cook_data}
### <<<<< Cook API <<<<< ###

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
