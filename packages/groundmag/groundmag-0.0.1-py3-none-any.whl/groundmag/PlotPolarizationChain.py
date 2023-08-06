import numpy as np
import matplotlib.pyplot as plt
from .PlotPolarization import PlotPolarization

def PlotPolarizationChain(Stations,Date,wind,slip,ut=None,high=None,low=None,Freq=None,comps=['x','y'],Threshold=0.0,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,fig=None,TimeAxisUnits='hh:mm',figsize=(8,11),Multiplier=1.0,trange=None,useytitle=True):
	'''
	'''
	#create the plot window if it doesn't already exist
	if fig is None:
		fig = plt
		fig.figure(figsize=figsize)
		
	#now work out the total number of stations to plot
	ns = np.size(Stations)
	
	#loop through each plot
	for i in range(0,ns):
		nox = i < (ns-1)
		ax = PlotPolarization(Stations[i],Date,wind,slip,ut=ut,high=high,low=low,Freq=Freq,comps=comps,Threshold=Threshold,Method=Method,WindowFunction=WindowFunction,Param=Param,Detrend=Detrend,FindGaps=FindGaps,fig=fig,maps=[1,ns,0,i],TimeAxisUnits=TimeAxisUnits,nox=nox,Multiplier=Multiplier,trange=trange,useytitle=useytitle)

		
	#remove space between subplots
	fig.subplots_adjust(hspace=0.0)
	
	
