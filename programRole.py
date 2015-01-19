import socket			# Needed to communicate hosts
import sqlite3			# Needed to access local database
import yahooDataObject	# Needed to access Yahoo data
import time				# For sleep


class MasterProgram:
	def __init__(self):
		self._objList = [yahooDataObject.yahooDataObject('GOOG'), 
				yahooDataObject.yahooDataObject('AAPL'),
				yahooDataObject.yahooDataObject('MSFT')]
		self._port = 12345					# Port for communication, private.
		self._slaveConnected = False 		# Tells if there is a slave connected
		self._listSock = socket.socket()	# Listener socket
		self._connSock = socket.socket()	# Connection socket
		self._host = socket.gethostname() 	# Get local machine name
		self._failCounter = 0				# Counts the number of failed attempts
		self._dbConn = sqlite3.connect('master.db') # Connect to master db
		self._dbCur = self._dbConn.cursor()	# Get cursor 

	def initConnection(self):
		self._listSock = socket.socket()
		self._listSock.settimeout(5.0) 		# Five seconds of timeout
		self._listSock.bind((self._host, self._port))
		self._listSock.listen(5) 			# Start receiving requests

	def doWork(self):
		while True:

			# Update data objects and database
			for obj in self._objList:
				obj.updateYahooStockQuoteWeb()
				obj.updateDataBase(self._dbCur)

			self._dbConn.commit()
		
			# Check for any new connection attempt
			if self._slaveConnected is False:
				try:
					self._connSock, addr = self._listSock.accept()
					self._connSock.setblocking(0)  # This socket is non-blocking
					self._connSock.settimeout(5.0) # Five seconds of timeout
					self._slaveConnected = True
					print "Connected to a slave"
					
				except socket.timeout:
					self._slaveConnected = False
					print "Couldnt connect to any slave"
					

			# Send data
			if self._slaveConnected is True:
				try:
					for i in [0, 1, 2]:
						self._connSock.send(self._objList[i].s + " ")
					self._failCounter = 0
					print "Packet sent"
				except (socket.timeout, socket.error):
					self._failCounter += 1
					if self._failCounter == 10:
						self._failCounter = 0
						self._slaveConnected = False
						self._listSock.close()	# Restart the socket
						self._connSock.close()	# Restart the socket
						self.initConnection()
						print "Restarting socket"


		


class SlaveProgram:
	def __init__(self, a_socket):
		self._objList = [yahooDataObject.yahooDataObject('GOOG'), 
				yahooDataObject.yahooDataObject('AAPL'),
				yahooDataObject.yahooDataObject('MSFT')]
		self._port = 12345 						# Port for communication, private.
		self._connStat = True					# Connection status
		self._connSock = a_socket 				# Connects with the master
		self._failCounter = 0					# Counts the number of failed attempts
		self._dbConn = sqlite3.connect('slave.db') # Connect to master db
		self._dbCur = self._dbConn.cursor()	# Get cursor 

	def doWork(self):
		self._connSock.settimeout(10.0) # Ten seconds timeout
		self._connSock.setblocking(0)		# Non-blocking socket

		while self._connStat is True: 	# While there is a Master

			# Receive data from server
			try:
				myData = self._connSock.recv(1024) ##################ESTO ES LO QUE HAY QUE ARREGLAR###############
				self._failCounter = 0
				cleanData = myData[:str.find(myData, ' ')] # Get only one sentence
														  # of data

				# Find out which object the slave received
				if str.find(cleanData, 'GOOG') != -1:
					ind = 0 # Google object
				elif str.find(cleanData, 'AAPL') != -1:
					ind = 1 # Apple object
				elif str.find(cleanData, 'MSFT') != -1:
					ind = 2 # Apple object
				else:
					ind = -1

				if ind != -1: # If could find any of those
					self._objList[ind].updateYahooStockQuoteStr(cleanData)
					# Update database
					self._objList[ind].updateDataBase(self._dbCur)
					self._dbConn.commit()


			except (socket.timeout, socket.error):
				time.sleep(4) # Four seconds of sleep
				self._failCounter += 1
				print self._failCounter
				if self._failCounter == 10:
					self._connStat = False
					self._connSock.close()

					


def testRole():
	s = socket.socket()         # Create a socket object
	host = socket.gethostname() # Get local machine name
	port = 12345                # Reserve a port for your service.
	try:
		s.connect((host, port))
		return s
	except socket.error:
		print "Couldn't find a server"
		return False
		
