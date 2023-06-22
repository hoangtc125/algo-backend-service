FROM python:3.8.16

WORKDIR /algo

COPY . /algo/

RUN pip install --upgrade wheel pip setuptools && \
    pip install -r requirements.txt
    # apt-get update && apt-get install -y zbar-tools

EXPOSE 8001

CMD ["bash", "command/server.sh"]
