import numpy as np
import matplotlib.pyplot as plt
from .PlotSpectrogram import PlotSpectrogram

def PlotSpectrogramChain(Stations,Date,wind,slip,ut=None,high=None,low=None,comp='Bx',Freq=None,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,GoodData=None,Quiet=True,LenW=None,fig=None,PlotType='Pow',scale=None,zlog=False,TimeAxisUnits='hh:mm',FreqAxisUnits='mHz',nolegend=False,figsize=(8,11),ylim=None):
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
		ax,_,_,_,_ = PlotSpectrogram(Stations[i],Date,wind,slip,ut=ut,high=high,low=low,comp=comp,Freq=Freq,Method=Method,WindowFunction=WindowFunction,Param=Param,Detrend=Detrend,FindGaps=FindGaps,GoodData=GoodData,Quiet=Quiet,LenW=LenW,fig=fig,maps=[1,ns,0,i],PlotType=PlotType,scale=scale,zlog=zlog,TimeAxisUnits=TimeAxisUnits,FreqAxisUnits=FreqAxisUnits,nox=nox)
		if not ylim is None:
			ax.set_ylim(ylim)
		
	#remove space between subplots
	fig.subplots_adjust(hspace=0.0)
	
	
