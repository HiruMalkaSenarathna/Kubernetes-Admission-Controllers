FROM python:3.9-slim

WORKDIR /app

COPY webhook_server.py .
COPY server.key .
COPY server.crt .

CMD ["python", "webhook_server.py"]
