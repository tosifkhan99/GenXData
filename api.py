from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.strategy_mapping import get_all_strategy_names, get_all_strategy_schemas
from exceptions.param_exceptions import InvalidConfigParamException
from main import start

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def catch_all_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # Log the exception for debugging
        print(e)
        # Return a generic 500 error response
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected internal server error occurred."},
        )



@app.get('/ping')
async def ping():
    return {"message": "pong"}


@app.get('/get_all_strategies')
async def get_all_strategies():
    return {"strategies": get_all_strategy_names()}


@app.get('/get_strategy_schemas')
async def get_strategy_schemas():
    return {"strategies": get_all_strategy_schemas()}


@app.post('/generate_data')
async def generate_data(config: Dict[str, Any]):
    return {"data": start(config)}


@app.post('/generate_config')
async def generate_config(config: Dict[str, Any]):
    return {"config": generate_config(config)}


@app.exception_handler(InvalidConfigParamException)
async def invalid_config_param_exception_handler(request: Request, exc: InvalidConfigParamException):
    return JSONResponse(
        status_code=400,
        content={"error_name": exc.name, "message": f"Oops! {exc.message}. We are on it!"},
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={"error_name": exc.name, "message": f"Something went wrong while generating data."},
    )
