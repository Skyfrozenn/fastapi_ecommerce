from fastapi import APIRouter


router = APIRouter(
    prefix="/products",
    tags=["Products_V2"]
)

@router.get("/")
async def new_products():
    return {"message" : "My new func for products"}