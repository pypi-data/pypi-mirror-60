import numpy as np
from . import Globals
import os

def _ReadBinary(Station,Date):
	'''
	Read binary mag data.
	
	'''
	
	#find out the input file name
	year = Date//10000
	ifile = Globals.DataPath + '{:04d}/{:08d}-{:s}.mag.gz'.format(year,Date,Station.upper())
	
	#copy file
	tfile = Globals.TmpPath + '{:08d}-{:s}.mag.gz'.format(Date,Station.upper())
	os.system('cp '+ifile+' '+tfile)
	
	#extract the archive
	os.system('gunzip '+tfile)

	#read the binary file
	bfile = Globals.TmpPath + '{:08d}-{:s}.mag'.format(Date,Station.upper())
	dtype = [('Date','int32'),('ut','float64'),('Bx','float64'),('By','float64'),('Bz','float64')]
	f = open(bfile,'rb')
	n = np.fromfile(f,dtype='int32',count=1)[0]
	data = np.recarray(n,dtype=dtype)
	data.Date = Date
	data.ut = np.fromfile(f,dtype='float64',count=n)
	data.Bx = np.fromfile(f,dtype='float64',count=n)
	data.By = np.fromfile(f,dtype='float64',count=n)
	data.Bz = np.fromfile(f,dtype='float64',count=n)
	f.close()
	
	#remove the file
	os.system('rm '+bfile)
	
	return data
