from .datatools import options, plot_options 
if options.manual_load:
	from .pkldata import PklData 
	from .txtdata import TxtData 
	from .hdf5data import Hdf5Data 
	from .hdf5data import Hdf5Data as Data
else:
	if options.files:
		if '.pkl' in options.files[0]:
			from .pkldata import PklData as Data
		elif '.hdf5' in options.files[0]:
			from .hdf5data import Hdf5Data as Data
		elif '.txt' in options.files[0]:
			from .txtdata import TxtData as Data

#define common symbols used in plot titles/axes/legends etc.
mu = '\u03bc'
deg = '\u03B1'
