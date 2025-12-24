from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import categories,products, users, reviews, cart, orders
from app.routers.statistics import products_stats,category_stats





app = FastAPI(
    title="Мое приложение на FastAPI",
    version="1.0"
)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(products_stats.router)
app.include_router(category_stats.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message" : "Добро пожаловать в Апи интернет магазина!"}