FROM python:3.12

LABEL maintainer="mustafa"

WORKDIR /code

COPY . /code/
 
RUN pip install uv

RUN uv add  "fastapi[standard]" uvicorn


CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"    ]
