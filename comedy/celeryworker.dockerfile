FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /comedy

COPY ./requirements.txt /comedy/requirements.txt

RUN pip install -r requirements.txt

COPY . /comedy

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]





