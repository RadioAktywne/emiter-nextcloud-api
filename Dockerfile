FROM python:3.9
ENV TZ Europe/Warsaw
RUN pip3 install fastapi uvicorn caldav icalendar
COPY *.py /api/
WORKDIR /api
ENTRYPOINT uvicorn main:app --host 0.0.0.0 --port 8000
