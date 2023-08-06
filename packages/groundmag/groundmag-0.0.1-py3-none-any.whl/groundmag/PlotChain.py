import numpy as np
import matplotlib.pyplot as plt
from .PlotData import PlotData

def PlotChain(Stations,Date,ut=None,fig=None,comp=['Bx','By','Bz','Bm'],high=None,low=None,useytitle=False,nolegend=False,figsize=(6,4),ylim=None,coords='hdz'):
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
		ax = PlotData(Stations[i],Date,ut=ut,fig=fig,maps=[1,ns,0,i],comp=comp,high=high,low=low,nox=nox,useytitle=useytitle,nolegend=nolegend,coords=coords)
		if not ylim is None:
			ax.set_ylim(ylim)
		
	#remove space between subplots
	fig.subplots_adjust(hspace=0.0)
	
	
