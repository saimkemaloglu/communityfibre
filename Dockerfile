FROM python:latest
ENV PYTHONUNBUFFERED 1
RUN mkdir /comfibdocker
WORKDIR /comfibdocker
COPY requirements.txt /comfibdocker/
RUN pip install -r requirements.txt
COPY . /comfibdocker/
EXPOSE 8000