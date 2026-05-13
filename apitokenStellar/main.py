#!/usr/bin/env python3

"""
apt install python3-pip
pip install fastapi
pip install "uvicorn[standard]"
pip install sqlalchemy
pip install email_validator
pip install sqlalchemy
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
pip install mysql-connector
pip install mysql-connector-python
pip install mysqlclient
pip install python-magic
pip install python-slugify
//para amazon aws
pip install mangum

para dejar el servidor uvicron corriendo en background
nos vamos a la carpeta donde esta el fichero main.py y ponemos
    nohup uvicorn main:app &
netstat -tulpn podemos ver si el proceso esta activo
tcp        0      0 127.0.0.1:8000          0.0.0.0:*               LISTEN      67474/python3
con el comando ps -A vemos los procesos, entre ellos el de uvicorn
67474 pts/0    00:00:01 uvicorn
y lo podemos matar con kill -9 PID
"""
import json
import logging
import re
import time
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.background import BackgroundTask
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import config
from api.v1.database import engine
from api.v1.models import models_invest, models_blockchain, models_user, models_governor
from api.v1.router import api_router

# to create database model
models_invest.Base.metadata.create_all(bind=engine)
models_blockchain.Base.metadata.create_all(bind=engine)
models_user.Base.metadata.create_all(bind=engine)
models_governor.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://127.0.0.1:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.middleware("http")
async def custom_access_log(request: Request, call_next):
    start_time = time.time()
    # Leer el cuerpo de la petición (payload)
    body = await request.body()
    # Volver a inyectar el cuerpo para que la app lo pueda leer después
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive

    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serializar headers y query params
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    
    # Get user from state if available
    user = getattr(request.state, "user", None)
    user_data = user.dict() if user and hasattr(user, "dict") else None
    
    # Decode request body
    request_body = None
    if body:
        try:
            body_str = body.decode("utf-8")
            request_body = obfuscate_sensitive_data(body_str)
        except UnicodeDecodeError:
            request_body = "<binary data>"

    log_payload = {
        "timestamp": now,
        "client_host": request.client.host,
        "method": request.method,
        "path": request.url.path,
        "http_version": request.scope["http_version"],
        "status_code": response.status_code,
        "process_time_ms": process_time,
        "headers": headers,
        "query_params": query_params,
        "referer": request.headers.get("referer", "-"),
        "user_agent": request.headers.get("user-agent", "-"),
        "user": user_data,
        "request_body": request_body
    }
    
    # Send log to local file in background
    if response.background:
        response.background.add_task(create_log_entry, log_payload)
    else:
        response.background = BackgroundTask(create_log_entry, log_payload)

    return response

def obfuscate_sensitive_data(body_str: str) -> str:
    SENSITIVE_KEYS = {'password', 'token', 'access_token', 'refresh_access_token', 'client_secret'}
    
    # Try parsing as JSON first
    try:
        data = json.loads(body_str)
        if isinstance(data, dict):
            for key in SENSITIVE_KEYS:
                if key in data:
                    data[key] = "******"
            return json.dumps(data)
    except json.JSONDecodeError:
        pass
    
    # Fallback to regex for form data or other strings
    # Looks for key=value patterns where key is in SENSITIVE_KEYS
    for key in SENSITIVE_KEYS:
        # 1. Match key=value (URL encoded)
        pattern_url = f'({key}=)([^&]*)'
        body_str = re.sub(pattern_url, r'\1******', body_str, flags=re.IGNORECASE)

        # 2. Match multipart/form-data
        # Busca: name="password" seguido de saltos de linea, el valor, y el siguiente boundary (o final)
        # Usamos re.DOTALL para que . coincida con saltos de linea si es necesario, pero aqui queremos capturar el valor
        # El formato es: name="key"\r\n\r\nvalue\r\n------boundary
        pattern_multipart = f'(name="{key}"\\s*\\r?\\n\\r?\\n)(.*?)(\\r?\\n------)'
        body_str = re.sub(pattern_multipart, r'\1******\3', body_str, flags=re.IGNORECASE | re.DOTALL)
        
    return body_str


logging.getLogger().setLevel(logging.INFO)
new_format = logging.Formatter('[%(asctime)s] %(levelname)s:%(message)s')
for handler in logging.root.handlers:
    handler.setFormatter(new_format)



# para que el log de error sea un poco mas detallado
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    date = f"{datetime.today().year}-{datetime.today().month}-{datetime.today().day} {datetime.today().hour}:{datetime.today().minute}.{datetime.today().second}"
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    print(f"date: {date} -> {request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    tasks = BackgroundTask(create_log_entry,
                           data={"date: ": date,
                                 "content": content, "response": exc.errors(), "request": exc.body}
                           )
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, background=tasks)


def create_log_entry(data):
    with open("log.txt", mode="a") as log:
        log.write(f"{data}\n")
