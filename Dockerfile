FROM python:3.11

WORKDIR /app

COPY ./scripts ./scripts
COPY ./.env .
COPY ./main.py .
COPY ./requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt


CMD ["python", "./main.py"]
