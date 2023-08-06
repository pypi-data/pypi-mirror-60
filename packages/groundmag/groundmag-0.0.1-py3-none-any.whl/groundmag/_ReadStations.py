import numpy as np
from . import Globals
import PyFileIO as pf

def _ReadStations(Network):
	'''
	Read the list of stations for a magnetometer network.
	
	'''
	fname = Globals.StationPath + Network + '.list'
	
	dtype = [('Code','U4'),('Station','object'),('Network','object'),
			('glat','float32'),('glon','float32'),('mlat','float32'),
			('mlon','float32'),('L','float32')]
	data = pf.ReadASCIIFile(fname)
	n = data.size

	out = np.recarray(n,dtype=dtype)
	
	for i in range(0,n):
		s = data[i].split()
		#the number of bits which are the name
		ln = len(s) - 6
		
		out[i].Code = s[0]
		out[i].Station = ' '.join(s[1:ln+1])
		out[i].glat = np.float32(s[1+ln])
		out[i].glon = np.float32(s[2+ln])
		out[i].mlat = np.float32(s[3+ln])
		out[i].mlon = np.float32(s[4+ln])
		out[i].L = np.float32(s[5+ln])
		
	out.Network[:] = Network

	return out
