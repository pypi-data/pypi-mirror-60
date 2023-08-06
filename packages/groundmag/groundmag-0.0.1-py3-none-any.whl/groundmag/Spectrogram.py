import numpy as np
import matplotlib.pyplot as plt
import wavespec as ws
from .GetData import GetData

def Spectrogram(Station,Date,wind,slip,ut=None,high=None,low=None,comp='Bx',Freq=None,Method='FFT',WindowFunction=None,Param=None,Detrend=True,FindGaps=True,GoodData=None,Quiet=True,LenW=None):
	
	
	#get the data
	data = GetData(Station,Date,ut,high,low)
	
	
	#get the spectrogram
	Nw,LenW,Freq,Spec = ws.Spectrogram.Spectrogram(data.utc*3600.0,data[comp],wind,slip,Freq,Method,WindowFunction,Param,Detrend,FindGaps,GoodData,Quiet,LenW)
	
	

	return Nw,LenW,Freq,Spec
