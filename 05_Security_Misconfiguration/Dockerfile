FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask
RUN echo "Flag{Security_Misconfiguration}" > /flag.txt

ENV WERKZEUG_DEBUG_PIN=1337
CMD ["python3", "app.py"]