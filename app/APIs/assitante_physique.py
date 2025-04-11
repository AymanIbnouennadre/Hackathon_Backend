from fastapi import APIRouter, Form

router = APIRouter()

@router.post("/")
async def say_hello(name: str = Form(...)):
    return {"message": f"hello {name}"}