#!/usr/bin/env python
import pickle


def loadEvents():
	try:
		dataFile = open('../data/eventsData.pkl', 'rb')
	except:
		return []
	eventList = pickle.load(dataFile)
	dataFile.close()
	return eventList


def saveEvents(eventList):
	try:
		dataFile = open('../data/eventsData.pkl', 'wb')
	except:
		print('Cannot save data on system.!\nCheck the given permission..')
	pickle.dump(eventList, dataFile)
	dataFile.close()
	return
	