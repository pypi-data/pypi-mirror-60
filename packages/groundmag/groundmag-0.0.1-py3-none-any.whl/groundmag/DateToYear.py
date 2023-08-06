import numpy as np
import DateTimeTools as TT

def DateToYear(Date):
	'''
	Converts the date from format yyyymmdd to yyyy.yy
	
	'''
	#get the year and day number from the date	
	yr = Date // 10000
	doy = TT.DayNo(Date)
	
	#check if there are leap years
	ly = np.int32(TT.LeapYear(Date))
	
	#work out total number of days in the year
	nd = 365.0 + ly
	
	#now work out the output
	year = yr + doy/nd
	
	return year
