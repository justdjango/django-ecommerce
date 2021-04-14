FROM python:3.9

WORKDIR /usr/src/app

EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [/bin/bash]
