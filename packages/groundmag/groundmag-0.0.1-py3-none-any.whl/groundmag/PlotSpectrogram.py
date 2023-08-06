import numpy as np
import matplotlib.pyplot as plt
import wavespec as ws
from .GetData import GetData

def PlotSpectrogram(Station,Date,wind,slip,ut=None,high=None,low=None,comp='Bx',Freq=None,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,GoodData=None,Quiet=True,LenW=None,fig=None,maps=[1,1,0,0],PlotType='Pow',scale=None,zlog=False,TimeAxisUnits='hh:mm',FreqAxisUnits='mHz',nox=False):
	
	
	#get the data
	data = GetData(Station,Date,ut,high,low)
	
	
	#plot the spectrogram
	ax,Nw,LenW,Freq,Spec = ws.Spectrogram.PlotSpectrogram(data.utc*3600.0,data[comp],wind,slip,Freq,Method,WindowFunction,Param,Detrend,FindGaps,GoodData,Quiet,LenW,fig,maps,PlotType,scale,zlog,TimeAxisUnits,FreqAxisUnits)
	
	#change the ylabel
	ax.set_ylabel('{:s}\n$f$ ({:s})'.format(Station.upper(),FreqAxisUnits))
	

	return ax,Nw,LenW,Freq,Spec
