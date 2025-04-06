from fastapi import FastAPI, Depends, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess, sys

from fastapi.responses import JSONResponse

from schemas import PostTodo, UserCreate, UserResponse, PromptHistoryCreate, PromptHistoryResponse, UserLogin
from models import TodoModel, User, Prompt_history
from settings import SessionLocal

from sqlalchemy.orm import Session

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

### >>>>> User API >>>>> ###
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # パスワードをハッシュ化
    hashed_password = pwd_context.hash(user.password)
    
    # ユーザーモデルの作成
    db_user = User(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        password_digest=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
### <<<<< User API <<<<< ###

### >>>>> Sign up API >>>>> ###
@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    hashed_password = pwd_context.hash(user.password)

    db_user = User(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        password_digest=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print("User created:", db_user.user_id)
    return JSONResponse(content={"message": "success"})
### <<<<< Sign up API <<<<< ###

### >>>>> Login API >>>>> ###
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None or not pwd_context.verify(user.password, db_user.password_digest):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return JSONResponse(content={"message": "success", "user_id": db_user.user_id})
### <<<<< Login API <<<<< ###
### >>>>> Prompt History API >>>>> ###
@app.post("/prompt-history", response_model=PromptHistoryResponse)
def create_prompt_history(
    prompt: PromptHistoryCreate,
    db: Session = Depends(get_db)
):
    db_prompt = Prompt_history(**prompt.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.get("/prompt-history/user/{user_id}", response_model=list[PromptHistoryResponse])
def get_user_prompt_history(user_id: str, db: Session = Depends(get_db)):
    prompts = db.query(Prompt_history).filter(Prompt_history.user_id == user_id).all()
    return prompts

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
