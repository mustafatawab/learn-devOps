from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message" : "working "}

@app.get("/health")
def health_check():
    return {"status" : "healthy"}