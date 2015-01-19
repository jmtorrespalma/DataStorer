import urllib2	#Needed to access Yahoo webpage

class yahooDataObject:
	""" Class to get values from Yahoo in different formats """

	""" Object constructor """
	def __init__(self, a_symbol):
		
		# Name of the object. Defines where to search
		self.symbol = a_symbol 
		# String formated data
		self.s = ""
		# Dictionary formated data
		self.D = {}

		self.updateYahooStockQuoteWeb()

	""" Returns a string, containing the values obtained from Yahoo """
	""" Also returns a dict, suitable to easily insert it in the DB """
	def updateYahooStockQuoteWeb(self):
		url = "http://download.finance.yahoo.com/d/" \
		"quotes.csv?s=%s&f=sl1d1c1hgv" % self.symbol
	
		f = urllib2.urlopen(url)
		s = f.read()
		f.close()

		s = s.strip()
		self.s = s.replace('"','')

		try:
			L = self.s.split(',')
		
			self.D['symbol'] = L[0]
			self.D['last'] = L[1]
			self.D['date'] = L[2]
			self.D['change'] = L[3]
			self.D['high'] = L[4]
			self.D['low'] = L[5]
			self.D['vol'] = L[6]
		except IndexError:
			self.D = {}

	""" Updates the object data using a string value """
	def updateYahooStockQuoteStr(self, string):

		self.s = string
		try:
			L = self.s.split(',')
		
			self.D['symbol'] = L[0]
			self.D['last'] = L[1]
			self.D['date'] = L[2]
			self.D['change'] = L[3]
			self.D['high'] = L[4]
			self.D['low'] = L[5]
			self.D['vol'] = L[6]
		except IndexError:
			self.D = {}


	def updateDataBase(self, cur):

		# First, we give format to string
		string = "'{}', ".format(self.D['symbol'])
		string = string + "{}, ".format(self.D['last'])
		string = string + "'{}', ".format(self.D['date'])
		string = string + "{}, ".format(self.D['change'])
		string = string + "{}, ".format(self.D['high'])
		string = string + "{}, ".format(self.D['low'])
		string = string + "{}".format(self.D['vol'])
	
		cur.execute('INSERT INTO data VALUES('+ string +')')
