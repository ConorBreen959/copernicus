FROM python:3.10-slim-buster

RUN apt-get update
RUN apt-get install -y  \
    && apt install tzdata -y

ENV TZ="Europe/Dublin"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "8000"]
