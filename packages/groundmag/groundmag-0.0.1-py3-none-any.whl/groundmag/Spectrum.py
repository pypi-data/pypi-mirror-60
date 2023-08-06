import numpy as np
import wavespec as ws
from .GetData import GetData

def Spectrum(Station,Date,ut=None,high=None,low=None,Method='FFT',WindowFunction=None,Param=None,Freq=None,comp=['Bx','By','Bz']):
	'''
	'''
	data = GetData(Station,Date,ut,high,low)
	
	if Freq is None and Method == 'LS':
		#we need frequencies here, so we will assume that the data are
		#evenly spaced and that we can use the FFT frequencies
		dt,ct = np.unique((data.utc[1:]-data.utc[:-1])*3600.0,return_counts=True)
		inter = dt[ct.argmax()]
		Freq = np.arange(data.size+1,dtype='float32')/(np.float32(data.size*inter))
	
	
	nc = np.size(comp)
	Pow = []
	Amp = []
	Pha = []
	Imag = []
	Real = []
	for i in range(0,nc):
		if Method == 'FFT':
			power,phase,Freq,fr,fi = ws.Fourier.FFT(data.utc*3600.0,data[comp[i]],WindowFunction,Param)
			amp = np.sqrt(power)
		else:
			power,phase,amp,fr,fi = ws.LombScargle.LombScargle(data.utc*3600.0,data[comp[i]],Freq,'C++',WindowFunction,Param)
		Pow.append(power)
		Amp.append(amp)
		Pha.append(phase)
		Imag.append(fi)
		Real.append(fr)
		
	if nc == 1:
		Pow = Pow[0]
		Amp = Amp[0]
		Pha = Pha[0]
		Real = Real[0]
		Imag = Imag[0]
		
	return Freq,Pow,Amp,Pha,Real,Imag
