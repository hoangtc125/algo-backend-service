FROM python:3.8.16

WORKDIR /algo

COPY requirements.txt /algo/requirements.txt

RUN pip install --upgrade wheel pip setuptools && \
    pip install -r requirements.txt
