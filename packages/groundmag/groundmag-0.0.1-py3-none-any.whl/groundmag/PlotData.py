import numpy as np
import matplotlib.pyplot as plt
import DateTimeTools as TT
from .UTPlotLabel import UTPlotLabel
from .GetStationInfo import GetStationInfo
from .GetData import GetData

def PlotData(Station,Date,ut=None,fig=None,maps=[1,1,0,0],comp=['Bx','By','Bz','Bm'],high=None,low=None,nox=False,useytitle=False,nolegend=False,coords='hdz'):
	'''
	
	'''
	
	
	#create title string
	stn = GetStationInfo(Station)
	title = Station.upper()
	pos = '(mlat={:3.1f},mlon={:3.1f})'.format(stn.mlat[0],stn.mlon[0])
	
	#Read data
	data = GetData(Station,Date,ut,high,low,coords=coords)
	
	
	#check if data are filtered
	if (not high is None) or (not low is None):
		dt,ct = np.unique((data.utc[1:]-data.utc[:-1])*3600.0,return_counts=True)
		inter = dt[ct.argmax()]
		if low is None:
			low = inter
		if high is None:
			high = inter
		filt = 'Filtered: low = {:3.1f} s, high = {:3.1f} s'.format(np.float32(low),np.float32(high))
	else:
		filt = None

	
	#cut the data down to within ut range
	if ut is None:
		ut = [0.0,24.0]
	
	if np.size(Date) == 2:
		utr = [ut[0],ut[1]+TT.DateDifference(Date[0],Date[1])*24.0]
	else:
		utr = ut


	
	#component label and color
	if coords == 'xyz':
		cmpcol = {	'Bx':	([1.0,0.0,0.0],'$B_x$'),
					'By':	([0.0,1.0,0.0],'$B_y$'),
					'Bz':	([0.0,0.0,1.0],'$B_z$'),
					'Bm':	([0.0,0.0,0.0],'$\pm|B|$')}
	else:
		cmpcol = {	'Bx':	([1.0,0.0,0.0],'$B_h$'),
					'By':	([0.0,1.0,0.0],'$B_d$'),
					'Bz':	([0.0,0.0,1.0],'$B_z$'),
					'Bm':	([0.0,0.0,0.0],'$\pm|B|$')}
	
	#create the plot window and axes
	if fig is None:
		fig = plt
		fig.figure()
	ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))

	#plot data
	if isinstance(comp,str):
		comp = [comp]
	nc = np.size(comp)
	for c in comp:
		B = data[c]
		col,lab = cmpcol[c]
		ax.plot(data.utc,B,color=col,label=lab)
		if c == 'Bm':
			ax.plot(data.utc,-B,color=col)
	
	#sort UT axis
	ax.set_xlim(utr)
	if nox:
		ax.xaxis.set_visible(False)
	else:
		UTPlotLabel(ax,'x')
		ax.set_xlabel('UT')
	
	#add the title
	if useytitle:
		ax.set_ylabel(title + '\n$B$ (nT)')	
		ax.text(0.02,0.97,pos,transform=ax.transAxes,va='top')
	else:
		ax.set_ylabel('$B$ (nT)')
		ax.text(0.02,0.97,title+' '+pos,transform=ax.transAxes,va='top')
		
	if not filt is None:
		ax.text(0.02,0.03,filt,transform=ax.transAxes,va='bottom')
	
	#legend
	if not nolegend:
		ax.legend(loc='upper right')
	
	return ax
