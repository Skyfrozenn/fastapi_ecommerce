from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware


from app.routers import categories,products, users, reviews, cart, orders, payments, products_v2
from app.routers.statistics import products_stats,category_stats

from time import time
from loguru import logger
from uuid import uuid4

logger.add("info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}]", level="INFO", enqueue = True)





app = FastAPI(
    title="Мое приложение на FastAPI",
    version="1.0"
)

@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                logger.warning(f"Request to {request.url.path} failed")
            else:
                logger.info('Successfully accessed ' + request.url.path)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        return response



app.add_middleware( #4
    GZipMiddleware,
    minimum_size = 1000,
    compresslevel=5
)

@app.middleware("http") #3
async def modify_request_response_middleware(request: Request, call_next):
    start_time = time() #текущее время
    response = await call_next(request) #некст мидлвар или приложение 
    duration = time() - start_time #смотрим время
    print(f"Request duration: {duration:.10f} seconds") #логирование
    return response  #возврат запроса


app.add_middleware( #2
    TrustedHostMiddleware,
    allowed_hosts = ["localhost", "127.0.0.1"] #разрешенные хосты
)

# app.add_middleware(HTTPSRedirectMiddleware) РЕДИРЕКТ НА https 

app.add_middleware( #1
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           
        "http://localhost:5173",           
    ],
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["Authorization", "Content-Type"] 
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
app.include_router(payments.router)
 
 



@app.get("/")
async def root():
    return {"message" : "Добро пожаловать в Апи интернет магазина!"}