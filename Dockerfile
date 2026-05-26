FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p media static/css static/js
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]