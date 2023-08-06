import numpy as np
import matplotlib.pyplot as plt
import wavespec as ws
from .Spectrogram3D import Spectrogram3D
from .GetStationInfo import GetStationInfo

def PlotPolarization(Station,Date,wind,slip,ut=None,high=None,low=None,Freq=None,comps=['x','y'],Threshold=0.0,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,fig=None,maps=[1,1,0,0],TimeAxisUnits='hh:mm',nox=False,Multiplier=1.0,trange=None,useytitle=False):

	#create title string
	stn = GetStationInfo(Station)
	title = Station.upper()
	pos = '(mlat={:3.1f},mlon={:3.1f})'.format(stn.mlat,stn.mlon)

	#check if data are filtered
	filt = 'Filtered: '
	if not low is None:
		filt += 'low = {:3.1f} s '.format(np.float32(low))
	if not high is None:
		filt += 'high = {:3.1f} s '.format(np.float32(high))
	if high is None and low is None:
		filt = None


	#get the spectrogram
	Nw,LenW,Freq,Spec = Spectrogram3D(Station,Date,wind,slip,ut=ut,high=high,low=low,Freq=Freq,Method=Method,WindowFunction=WindowFunction,Param=Param,Detrend=Detrend,FindGaps=FindGaps,GoodData=None)
	
	#combine the appropriate components
	P = Spec[comps[0]+'Pow'] + Spec[comps[1]+'Pow']
	
	#now find the most powerful peak along the time axis
	pk = ws.DetectWaves.DetectWavePeaks(Spec.Tspec,Freq,P,Threshold,True)
	
	#get the amplitudes and phases
	Ax = Spec.xAmp[pk.tind,pk.find]
	Px = Spec.xPha[pk.tind,pk.find]
	
	Ay = Spec.yAmp[pk.tind,pk.find]
	Py = Spec.yPha[pk.tind,pk.find]
	
	Az = Spec.zAmp[pk.tind,pk.find]
	Pz = Spec.zPha[pk.tind,pk.find]
	
	Dir = Spec.kz[pk.tind,pk.find]
	

	#plot the polarization ellipses
	ax = ws.Tools.PlotPolarization(pk.t,Ax,Ay,Px,Py,Dir,fig=fig,maps=maps,Multiplier=Multiplier,nox=False,trange=None,TimeAxisUnits=TimeAxisUnits)
	
	#add the title
	if useytitle:
		ax.set_ylabel(title)	
		ax.text(0.02,0.97,pos,transform=ax.transAxes,va='top')
	else:
		ax.text(0.02,0.97,title+' '+pos,transform=ax.transAxes,va='top')
		
	if not filt is None:
		ax.text(0.02,0.03,filt,transform=ax.transAxes,va='bottom')
	
	
	return ax
