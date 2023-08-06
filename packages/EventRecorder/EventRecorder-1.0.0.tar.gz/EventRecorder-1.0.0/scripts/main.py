#!/usr/bin/env python

import sys,os
# sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import argparse
import datetime
import functools
import pprint
import time
from pickling import loadEvents, saveEvents
from filterSearch import extractForRange, extractForSpecificDate, \
extractForToday, deleteEventOn
eventList = []


#Event class
class Event:
	def __init__(self, title, eDate, desc):
		self.title = title
		self.eDate = eDate
		self.eDesc = desc
	def __str__(self):
		return('Title: {}\nDate & Time: {}\nDescription:{}\n'\
			.format(self.title, time.asctime(self.eDate), self.eDesc))

def loadDataDump():
	eventList.extend(loadEvents())

def saveDataDump():
	saveEvents(eventList)


def addEvent(eventList):
	''' add an event '''
	eTitle = input('Enter Event Title: ')
	eDate = input('Enter Event Date and Time, format example 30 Nov 2020, 23:10: ')
	eDesc = input('Enter Event Description: ')
	try:
		event = Event(eTitle, time.strptime(eDate, "%d %b %Y, %H:%M"), eDesc)
	except:
		print('Wrong format, please try again')
	yetFl = True
	for idx in range(len(eventList)):
		if(time.mktime(eventList[idx].eDate) > time.mktime(event.eDate)):
			eventList = eventList[:idx] + [event] + eventList[idx:]
			yetFl = False
			break
	if(yetFl):
		eventList.append(event)
		return eventList
	return eventList
	
def viewAll(events):
	''' prints all events '''
	for event in events:
		viewOne(event)

def viewOne(event):
	''' prints a single event '''
	print('Title: {}\nDate & Time: {}\nDescription: {}\n'\
		.format(event.title, time.asctime(event.eDate), event.eDesc))

def compareEvents(e1, e2):
	return (time.mktime(e1.eDate) - time.mktime(e2.eDate))

#---------------------------------Set up---------------------------------------
loadDataDump()
parser = argparse.ArgumentParser(description = 'Event Reminder Utility')

# parser.add_argument('--add', action = 'store_true', help = 'flag to add an event reminder')
parser.add_argument('--today', action = 'store_true', help = 'flag to display all events for today')
parser.add_argument('--delete', action = 'store_true', help = 'flag to delete an event')
parser.add_argument('--for-date', help = 'events for a specific given date (format: dd-mm-yyyy)')
parser.add_argument('--range', default = False, help = \
'two dates separated by space as range to extract events from (format: dd-mm-yyyy)')
parser.add_argument('--view-all', action = 'store_true', help = 'display all the events from today')

args = vars(parser.parse_args())

if args.get('today'):
	events = extractForToday(eventList)
	viewAll(events)

elif args.get('view_all'):
	viewAll(eventList)

elif args.get('delete'):
	dDate = input('Enter the date (format: dd-mm-yyyy) of the event to be deleted: ')
	resList = deleteEventOn(dDate, eventList)
	eventList = resList[0]
	if(resList[1]):
		eventList.sort(key = functools.cmp_to_key(compareEvents))
		print("deleted succesfully")
		saveDataDump()

elif args.get('for_date'):
	events = extractForSpecificDate(args.get('for_date'), eventList)
	viewAll(events)

elif args.get('range'):
	datesStr = args.get('range')
	dateL = datesStr.split()
	date1 = dateL[0]
	date2 = dateL[1]
	events = extractForRange(date1, date2, eventList)
	viewAll(events)
	
else:
	eventList = addEvent(eventList)
	print('Event added Successfully')
	saveDataDump()