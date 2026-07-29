FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen

COPY . .

EXPOSE 8000

LABEL NAME="FastAPI App"  VERSION="1.0.1" DESCRIPTION="Sample app to test docker" AUTHOR='Mustafa Tawab'

CMD ["uv" , "run" , "uvicorn" , "main:app" , "--host" , "0.0.0.0" , "--port" , "8000" , "--reload"]