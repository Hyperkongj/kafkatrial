FROM python:3.9

WORKDIR /app/consumer

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/consumer"

CMD ["python", "main.py"]
