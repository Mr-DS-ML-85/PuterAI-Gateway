FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*      
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE $HOST_PORT
CMD ["python3", "server.py"]
