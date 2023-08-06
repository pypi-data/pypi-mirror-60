#!/usr/bin/env python
import time
import datetime
import calendar


def extractForToday(eventList):
	''' Extracting events for today '''
	today_struct = time.strptime(datetime.date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
	resList = filter(lambda event : 
		(event.eDate.tm_year == today_struct.tm_year and \
			event.eDate.tm_mon == today_struct.tm_mon and event.eDate.tm_mday == today_struct.tm_mday),
		eventList)
	return resList


def extractForSpecificDate(dateStr, eventList):
	''' Extracting events for a specific date '''
	date_struct = time.strptime(dateStr, "%d-%m-%Y")
	resList = filter(lambda event : 
		(event.eDate.tm_year == date_struct.tm_year and \
			event.eDate.tm_mon == date_struct.tm_mon and event.eDate.tm_mday == date_struct.tm_mday),
		eventList)
	return resList

def extractForRange(dateStr1, dateStr2, eventList):
	''' Extracting events for a range of dates '''
	date1_struct = time.strptime(dateStr1, "%d-%m-%Y")
	date2_struct = time.strptime(dateStr2, "%d-%m-%Y")
	resList = filter(lambda event : 
		(time.mktime(event.eDate) > time.mktime(date1_struct) and time.mktime(event.eDate) < time.mktime(date2_struct)),
		eventList)
	return resList

def deleteEventOn(dDate, eventList):
	''' delete events for a specific date '''
	date_struct = time.strptime(dDate, "%d-%m-%Y")
	filterList = []
	remList = []
	for event in eventList:
		if(event.eDate.tm_year == date_struct.tm_year and \
		event.eDate.tm_mon == date_struct.tm_mon and \
		event.eDate.tm_mday == date_struct.tm_mday):
			filterList.append(event)
		else:
			remList.append(event)
	if(len(filterList) == 0):
		print("No events on given date")
		return [eventList, False]
	idx = 1
	for event in filterList:
		print(str(idx) + '. Title: {}\nDate & Time: {}\nDescription: {}\n'\
		.format(event.title, time.asctime(event.eDate), event.eDesc))
		idx += 1
	deletionIdx = map(int, input('Enter sequence number(s) for events to be' +\
		' deleted(you can enter multiple numbers separated by space): '))
	for idx in deletionIdx:
		del filterList[idx - 1]
	return [remList + filterList, True]