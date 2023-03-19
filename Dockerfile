FROM python:3.9
RUN apk update && apk add git

RUN mkdir /app
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "/app/tts_service.py", "-p", "5000:5000"]