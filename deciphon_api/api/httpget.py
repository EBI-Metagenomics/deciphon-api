from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def httpget():
    return {"msg": "Hello World"}
