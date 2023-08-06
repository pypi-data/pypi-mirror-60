import numpy as np
import wavespec as ws
from .GetData import GetData

def Spectrogram3D(Station,Date,wind,slip,ut=None,high=None,low=None,Freq=None,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,GoodData=None):
	
	
	#get the data
	data = GetData(Station,Date,ut,high,low)
	
	#get the spectrogram
	Nw,LenW,Freq,Spec = ws.Spectrogram.Spectrogram3D(data.utc*3600.0,data.Bx,data.By,data.Bz,wind,slip,Freq=Freq,Method=Method,WindowFunction=WindowFunction,Param=Param,Detrend=Detrend,FindGaps=FindGaps,GoodData=GoodData)


	return Nw,LenW,Freq,Spec
