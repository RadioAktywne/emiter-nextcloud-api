from fastapi import FastAPI
import caldav_schedule as schedule
import logging

logging.basicConfig(level=logging.INFO)

cal = schedule.CalendarAPI()
app = FastAPI()

@app.get("/hello")
def hello():
    return("Hello")


@app.get("/timeslots")
def get_timeslots():
    cal.refresh()
    return cal.timeslots