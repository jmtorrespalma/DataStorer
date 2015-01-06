import socket						# Needed to communicate hosts
import sqlite3					# Needed to access local database
import yahooDataObject	# Needed to access Yahoo data
import time							# For sleep


class MasterProgram:
	def __init__(self):
		self._objList = [yahooDataObject.yahooDataObject('GOOG'), 
											yahooDataObject.yahooDataObject('AAPL'),
											yahooDataObject.yahooDataObject('MSFT')]
		self._port = 12345								# Port for communication, private.
		self._slaveConnected = False 			# Tells if there is a slave connected
		self._listSock = socket.socket()	# Listener socket
		self._connSock = socket.socket()	# Connection socket
		self._host = socket.gethostname() # Get local machine name
		self._failCounter = 0							# Counts the number of failed attempts

	def initConnection(self):
		self._listSock = socket.socket()
		self._listSock.settimeout(5.0) # Five seconds of timeout
		self._listSock.bind((self._host, self._port))
		self._listSock.listen(5) # Start receiving requests

	def doWork(self):
		while True:

			# Update data objects
			for obj in self._objList:
				obj.updateYahooStockQuoteWeb()
		
			# Check for any new connection attempt
			if self._slaveConnected is False:
				try:
					self._connSock, addr = self._listSock.accept()
					self._connSock.settimeout(5.0) # Five seconds of timeout
					self._slaveConnected = True
					self._connSock.setblocking(0)  # This socket is non-blocking
					print "Connected to a slave"
					
				except socket.timeout:
					self._slaveConnected = False
					print "Couldnt connect to any slave"
					

			# Send data
			if self._slaveConnected is True:
				try:
					self._connSock.send(self._objList[0].s)
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

			# Update database

		


class SlaveProgram:
	def __init__(self, a_socket):
		self._objList = [yahooDataObject.yahooDataObject('GOOG'), 
											yahooDataObject.yahooDataObject('AAPL'),
											yahooDataObject.yahooDataObject('MSFT')]
		self._port = 12345 								# Port for communication, private.
		self._connStat = True							# Connection status
		self._connSock = a_socket 				# Connects with the master
		self._failCounter = 0							# Counts the number of failed attempts

	def doWork(self):
		self._connSock.settimeout(10.0) # Ten seconds timeout
		self._connSock.setblocking(0)		# Non-blocking socket

		while self._connStat is True: 	# While there is a Master

			# Receive data from server
			try:
				myData = self._connSock.recv(1024) ##################ESTO ES LO QUE HAY QUE ARREGLAR###############
				self._objList[0].updateYahooStockQuoteStr(myData)
				self._failCounter = 0
			except (socket.timeout, socket.error):
				time.sleep(4) # Four seconds of sleep
				self._failCounter += 1
				print self._failCounter
				if self._failCounter == 10:
					self._connStat = False
					self._connSock.close()

		# Update objects

		# Update database


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
		
