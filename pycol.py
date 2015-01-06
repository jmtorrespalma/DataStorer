#!/bin/python2.7

import socket	#Needed to communicate hosts
import urllib2	#Needed to access Yahoo webpage
import sqlite3	#Needed to access local database

import yahooDataObject
import programRole

""" ########## The main program starts here ######### """

""" First thing to do is check if initializate the connection """

role = programRole.testRole()

if role is not False: # If it's a slave
	print "I'm a slave"
	program = programRole.SlaveProgram(role)
	program.doWork()
	print "Becoming a master"

program = programRole.MasterProgram()
program.initConnection()
program.doWork()


