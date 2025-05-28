FROM python:3.12
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      firefox-esr \
      ca-certificates \
      fonts-liberation \
      libgtk-3-0 \
      libdbus-glib-1-2 \
      libasound2 && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
