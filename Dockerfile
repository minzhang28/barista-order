FROM python:3.6-slim

RUN apt-get update && apt-get install -y curl
COPY requirements.txt /opt/barista-order/requirements.txt
RUN cd /opt/barista-order && pip install -r requirements.txt
COPY . /opt/barista-order/
WORKDIR /opt/barista-order
HEALTHCHECK CMD curl -f http://localhost:5000 || exit 1
EXPOSE 5000
CMD gunicorn -b 0.0.0.0:5000 app:app
