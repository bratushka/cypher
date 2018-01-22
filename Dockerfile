FROM python:alpine3.6

RUN apk add --no-cache --virtual build-essentials \
    musl-dev \
    gcc \
    git \
    postgresql-dev \
    python3-dev \
    make

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
