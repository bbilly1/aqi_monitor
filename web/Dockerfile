FROM python

COPY . /srv/flask_app
WORKDIR /srv/flask_app

RUN mkdir -p static/dyn/monthly
RUN chmod 777 -R .

RUN apt-get clean && apt-get -y update

RUN apt-get -y install python3-dev \
    && apt-get -y install build-essential

RUN pip install -r requirements.txt --src /usr/local/src


RUN chmod +x ./start.sh

CMD ["./start.sh"]
