import numpy as np
import os

ModulePath = os.path.dirname(__file__)+'/'
StationPath = ModulePath+'__data/'
try:
	DataPath = os.getenv('GROUNDMAG_DATA')+'/'
except:
	DataPath = ''
	print('Please set $GROUNDMAG_DATA')
TmpPath = os.getenv('HOME')+'/.tmp/'
if not os.path.isdir(TmpPath):
	os.system('mkdir -pv '+TmpPath)


Stations = None


Data = {}
