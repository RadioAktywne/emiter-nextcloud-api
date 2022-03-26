import icalendar
import caldav
from fastapi import FastAPI

import time as t
from datetime import datetime,timedelta,date,time
import json
import logging

import config

logging.basicConfig(level=logging.INFO)

class CalendarAPI:

    timeslots = {}
    programs = {}
    slug_uids = {}

    #default time to live in seconds
    default_ttl = 3*60
    ttl_stamp = 0

    def __init__(self) -> None:

        self.client = caldav.DAVClient(url=config.url,username=config.user,password=config.passwd)
        self.refresh()

    def refresh(self,ttl=None):

        if ttl is None:
            ttl = self.default_ttl

        ##ignore when refreshed yet
        now = t.time()

        if now - self.ttl_stamp < ttl:
            logging.info("last update was %d mins ago, ignored" % ((now-self.ttl_stamp)/60))
            return

        self.ttl_stamp = now

        d_from = datetime.combine(date.today(),time())
        d_to = d_from+timedelta(days=7)

        live_timeslots = self.get_slots_from_cal(self.client.calendar(url=config.url+"/calendars/"+config.user+"/emiter_audycje"),d_from,d_to)
        replay_timeslots = self.get_slots_from_cal(self.client.calendar(url=config.url+"/calendars/"+config.user+"/emiter_powtorki"),d_from,d_to)

        logging.info("found %d live shows and %d replays." % (len(live_timeslots),len(replay_timeslots)))

        #print(live_timeslots)
        #print(replay_timeslots)


        #parse live shows (and programs)
        for slot in live_timeslots:

            #skip if there is no summary (slug)
            if type(slot["summary"]) is not str:
                continue

            slug = slot["summary"]
            name = slot["description"]
            rds = slot["location"]
            uid = slot["uid"]

            #check if there is an UID in list
            if slug in self.slug_uids.keys():
                pgm_uid = self.slug_uids[slug]
            else:
                pgm_uid = slot["uid"]
                self.slug_uids[slug] = pgm_uid

            #set name and RDS
            if type(name) is not str:
                logging.warning("program '%s' does not have name defined. Using default (%s)" % (slug, slug))
                name = slug

            if type(rds) is not str:
                logging.warning("program '%s' does not have RDS defined. Using default (%s)" % (slug, name))
                rds = name

            #add a new program
            self.programs[pgm_uid] = {
                "slug": slug,
                "name": name,
                "rds": rds,
                "broadcast_visible": True
            }

            #get timeslot data (weekday, begin hr and min, duration)
            wd,h,m = self.dt_to_whm(slot["start"])
            duration = slot["duration"]

            self.timeslots[uid] = {
                "weekday":wd,
                "begin_h":h,
                "begin_m":m,
                "duration":duration,
                "program": self.programs[pgm_uid],
                "replay":False
            }

        #parse replays
        for slot in replay_timeslots:
            #skip if there is no summary (slug)
            if type(slot["summary"]) is not str:
                continue

            #get slug and uid
            slug = slot["summary"]
            uid = slot["uid"]

            #skip if slug is not in programs (replay, but not live show)
            if slug not in self.slug_uids.keys():
                logging.warning("Cannot find '%s' in live program list" % slot["summary"])
                continue
                

            pgm_uid = self.slug_uids[slug]

            #get timeslot data (weekday, begin hr and min, duration)
            wd,h,m = self.dt_to_whm(slot["start"])
            duration = slot["duration"]

            self.timeslots[uid] = {
                "weekday":wd,
                "begin_h":h,
                "begin_m":m,
                "duration":duration,
                "program": self.programs[pgm_uid],
                "replay":True
            }


    def vtext_to_str(self,v):
        if type(v) is icalendar.vText:
            return str(v)
        else:
            return None

    def get_slots_from_cal(self,cal,d_from,d_to):

        events = cal.date_search(d_from,d_to)

        cal_slots = []
        for event in events:
            for evt_payload in event.icalendar_instance.walk():
                if evt_payload.name == "VEVENT":
                    
                    tfrom = evt_payload.get('dtstart').dt.astimezone(tz=None)
                    tto = evt_payload.get('dtend').dt.astimezone(tz=None)
            
                    #program duration
                    delta = tto-tfrom
                    duration = round(delta.total_seconds()/60)
                    
                    cal_slots.append({
                        "uid": self.vtext_to_str(evt_payload.get('uid')),
                        "summary": self.vtext_to_str(evt_payload.get('summary')),
                        "description": self.vtext_to_str(evt_payload.get('description')),
                        "location": self.vtext_to_str(evt_payload.get('location')),
                        "start": tfrom,
                        "duration": duration
                    })
        
        return cal_slots


    def dt_to_whm(self,dt):
        """
            Gets weekday,hour and min from datetime
        """
        return dt.isoweekday(), dt.hour, dt.minute


