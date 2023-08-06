import numpy as np
from .ReadData import ReadData
import DateTimeTools as TT

def GetData(Station,Date,ut=None,high=None,low=None,coords='hdz'):
	
	#Read data
	data = ReadData(Station,Date,coords)
	
	#create output array
	dtype = [('Date','int32'),('ut','float64'),('utc','float64'),
			('Bx','float64'),('By','float64'),('Bz','float64'),('Bm','float64')]
	out = np.recarray(data.size,dtype=dtype)
	out.Date = data.Date
	out.ut = data.ut
	out.utc = data.ut
	out.Bx = data.Bx
	out.By = data.By
	out.Bz = data.Bz
	
	#create a continuous time axis
	ud = np.unique(data.Date)
	nd = ud.size
	for i in range(0,nd):
		dd = TT.DateDifference(ud[0],ud[i])
		use = np.where(data.Date == ud[i])[0]
		out.utc[use] += dd*24.0
	
	
	#filter data
	if (not high is None) or (not low is None):
		dt,ct = np.unique((out.utc[1:]-out.utc[:-1])*3600.0,return_counts=True)
		inter = dt[ct.argmax()]
		if low is None:
			low = inter
		if high is None:
			high = inter
		out.Bx = TT.lsfilter(data.Bx,high,low,inter)
		out.By = TT.lsfilter(data.By,high,low,inter)
		out.Bz = TT.lsfilter(data.Bz,high,low,inter)

	#cut the data down to within ut range
	if not ut is None:
		if np.size(Date) == 2:
			utr = [ut[0],ut[1]+TT.DateDifference(Date[0],Date[1])*24.0]
			use = np.where((utc >= utr[0]) & (utc <= utr[1]))[0]
		else:
			use = np.where((data.ut >= ut[0]) & (data.ut <= ut[1]))[0]
			utr = ut
		out = out[use]


	#calculate the magnitude
	out.Bm = np.sqrt(out.Bx**2 + out.By**2 + out.Bz**2)

	return out
