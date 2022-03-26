from fastapi import FastAPI
import caldav_schedule as schedule
import logging

logging.basicConfig(level=logging.INFO)

cal = schedule.CalendarAPI()
app = FastAPI()

#just for debug process
@app.get("/hello")
def hello():
    return("Hello")

#get all timeslots
@app.get("/timeslots")
def get_timeslots():
    cal.refresh()
    return cal.timeslots

#get single slot
@app.get("/timeslots/{uid}")
def get_single_timeslot(uid):
    cal.refresh()
    return cal.timeslots[uid]

#get all PGMs
@app.get("/programs")
def get_programs():
    cal.refresh()
    return cal.programs

#get single PGM
@app.get("/programs/{uid}")
def get_single_program(uid):
    cal.refresh()
    return cal.programs[uid]