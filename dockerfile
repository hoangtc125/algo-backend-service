FROM python:3.8.16

WORKDIR /algo

COPY . /algo/

RUN pip install --upgrade wheel pip setuptools
RUN pip install -r requirements.txt
RUN apt-get install zbar-tools

EXPOSE 8001

CMD ["bash", "command/server.sh"]
