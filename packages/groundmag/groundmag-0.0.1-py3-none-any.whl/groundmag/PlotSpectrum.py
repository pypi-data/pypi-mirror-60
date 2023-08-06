import numpy as np
import matplotlib.pyplot as plt
from .Spectrum import Spectrum

def PlotSpectrum(Station,Date,ut=None,high=None,low=None,Method='FFT',WindowFunction=None,Param=None,Freq=None,comp=['Bx','By','Bz'],PlotType='power',FreqAxisUnits='Hz',fig=None,maps=[1,1,0,0]):
	
	#get the spectra
	Freq,Pow,Amp,Pha,Real,Imag = Spectrum(Station,Date,ut,high,low,Method,WindowFunction,Param,Freq,comp)

	#set the frequency
	if FreqAxisUnits == 'Hz':
		f = Freq
	elif FreqAxisUnits == 'mHz':
		f = Freq*1000.0
	else:
		print('Frequency axis units {:s} not recognised, defaulting to "Hz"'.format(FreqAxisUnits))
		f = Freq
	
	#select the parameter to plot
	plotparams = {	'power':	(Pow,'Power'),
					'phase':	(Pha,'Phase'),
					'amplitude':	(Amp,'Amplitude'),
					'real':		(Real,'Real'),
					'imaginary':	(Imag,'Imaginary')}
	P,ylabel = plotparams[PlotType]
	
	#create the figure
	if fig is None:
		fig = plt
		fig.figure()
	ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))

	#component label and color
	cmpcol = {	'Bx':	([1.0,0.0,0.0],'$B_x$'),
				'By':	([0.0,1.0,0.0],'$B_y$'),
				'Bz':	([0.0,0.0,1.0],'$B_z$')}

	#plot each component
	nc = np.size(comp)
	if nc == 1:
		P = [P]
	l = np.min([np.size(P[0]),np.size(f)])
	for i in range(0,nc):
		c,lab = cmpcol[comp[i]]
		ax.plot(f[:l],P[i][:l],color=c,label=lab)
		
	
	ax.legend()

	#axis labels
	ax.set_ylabel(ylabel)
	ax.set_xlabel('Frequency, $f$ ('+FreqAxisUnits+')')
