FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir Flask==2.0.3 Werkzeug==2.0.3 PyYAML==5.3.1
RUN echo "Flag{Vulnerable_and_Outdated_Components}" > /flag.txt && chmod 600 /flag.txt

ENV FLASK_APP=app.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
