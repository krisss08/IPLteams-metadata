import uvicorn 
from fastapi import FastAPI
from app import api_router

description = "CRUDL APIs for IPL Teams Dataset. Enjoy"

app = FastAPI(title="IPL Team Dataset", description= description)

app.include_router(api_router)

@app.get("/")
def ping():
    return {"message": "Hello there, welcome. Enjoy building the Starfire APIs !! 🧸"}


@app.get("/ping")
def ping():
    return {"message": "Pong Test"}


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

