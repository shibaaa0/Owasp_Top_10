FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask
RUN echo "Flag{Injection}" > /flag.txt

CMD ["python3", "app.py"]