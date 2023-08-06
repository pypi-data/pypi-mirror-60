import numpy as np
import pyIGRF
from .DateToYear import DateToYear

def hdz2xyz(h,d,z,Date,lat,lon,alt=0.0):
	'''
	converts H,D,Z coordinates to X,Y,Z using the IGRF model to get the
	magnetic declination.
	
	'''

	#get the year
	year = DateToYear(Date)
	
	#find unique year/lat/lon combinations
	n = np.size(h)
	dlla = np.zeros((4,n),dtype='float32')
	dlla[0] = year
	dlla[1] = lat
	dlla[2] = lon
	dlla[3] = alt
	udlla = np.unique(dlla,axis=1)
	
	#get the declination
	nu = np.size(udlla[0])
	dec = np.zeros(n,dtype='float32')
	for i in range(0,nu):
		dc,_,_,_,_,_,_ = pyIGRF.igrf_value(udlla[0,i],udlla[1,i],udlla[2,i],udlla[3,i])
		comp = (dlla.T == udlla.T[i]).all(axis=1)
		use = np.where(comp)[0]
		dec[use] = dc
	
	
	#rotate x and y
	dec = dec*np.pi/180.0
	x = h*np.cos(-dec) + d*np.sin(-dec)
	y = h*np.sin(-dec) - d*np.cos(-dec)
	
	return x,y,z
