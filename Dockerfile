FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
