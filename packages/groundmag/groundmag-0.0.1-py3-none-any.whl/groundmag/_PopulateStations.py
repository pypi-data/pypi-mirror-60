import numpy as np
from ._ReadStations import _ReadStations
import RecarrayTools as RT
from . import Globals

def _PopulateStations():
	
	data = None
	Networks = ['carisma','image','intermagnet','supermag']
	
	for net in Networks:
		tmp = _ReadStations(net)
		if data is None:
			data = tmp
		else:
			data = RT.JoinRecarray(data,tmp)
	
	Globals.Stations = data
