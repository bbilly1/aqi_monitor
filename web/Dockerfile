FROM python:3.11.3-slim-bullseye

RUN apt-get clean && apt-get -y update && \
    apt-get -y install --no-install-recommends build-essential

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt --src /usr/local/src

COPY . /srv/flask_app
WORKDIR /srv/flask_app

RUN mkdir -p static/dyn/monthly
RUN chmod 777 -R .

RUN chmod +x ./start.sh

CMD ["./start.sh"]
