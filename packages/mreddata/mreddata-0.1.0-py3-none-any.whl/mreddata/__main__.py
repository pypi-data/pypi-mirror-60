import h5py as hp
import numpy as np
import pandas as pd
import argparse, sys, os
import matplotlib.pyplot as plt

def resetOptions():                                                                                                                                       
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', '-d', type=str, default='.', help='Directory path for the HDF5 files. All files should be in the same directory (defaults to the current working directory)')  #TODO: add features for combining files from several folders
    parser.add_argument('-a', '--all', action='store_true', default=False, help='Automatically gather all of the histograms from all HDF5 **files** in the working directory. Returns dictionary object sorted by filename and then histogram name')
    parser.add_argument('-f', '--files' , type=str, nargs="+", default=[], help='Only load data from the HDF5 files listed after this flag (rather than every HDF5 in the directory)')
    parser.add_argument('--raw', action='store_true', default=False, help='only return the raw data, with no normalization / post processing applied (default is normalized the gun fluence unit and nIons)')
    parser.add_argument('--diff', action='store_true', default=False, help='differntial data (default is reverse-integrated)')
    parser.add_argument('-l', '--load', action='store_true', default=False, help='Load all of the histograms in the file into memory. Not a good idea for files with large amounts of histograms')
    options, __remaining = parser.parse_known_args(sys.argv[1:])
    return options

options = resetOptions()
options.directory = options.directory +'/' if options.directory[-1] != '/' else options.directory

####################
# \class _NameMgr
class _NameMgr:
	def __init__(self, listIn = []):
		self.names = listIn
		self._reset = listIn

	def __repr__(self):
		return "\n-----------------------------\nCurrent items: \n{}\n-----------------------------".format(str(self.names))

	def dropNames(self, dropFilters, exact = False):
		'''Updates the names file list, droppinng files which match the filterString(s).'''
		if type(dropFilters) == list:
			for dropFilter in dropFilters:
				self.dropNames(dropFilter, exact = exact)
		else:
			if exact:
				selected = [f for f in self.names if dropFilters != f]
			else:
				selected = [f for f in self.names if dropFilters not in f]
			self.names = selected

	def selectNames(self, selectFilters, exact = False):
		'''Updates the names file list to only include those file(s) which match the filterString(s)'''
		if type(selectFilters) == list:
			for selectFilter in selectFilters:
				self.selectNames(selectFilter, exact = exact)
		else:
			if exact:
				selected = [f for f in self.names if selectFilters == f]
			else:
				selected =  [f for f in self.names if selectFilters in f]
			self.names = selected

	def resetNames(self):
		self.names = self._reset



class Histogram:
	def __init__(self, df, histname, filename, label=None, color=None):
		self.df = df
		self.filename = filename
		self.name = histname 
		self.label = label if label else self.df.name
		self.color = color 
	#TODO: add set label method
# develop method for passing a list of labels (MAYBE in plotHistograms arguments for Hdf5Data class? ) to allow an overwrite manually of the labels for histogram objects 
	
	def __repr__(self):
		return self.filename + " / " + self.name
		#return "===========================\nHistogram object. Name: {} Data:\n{}".format(self.name, self.df)

	def revInt(self):
		'''"Reverse Integrates" the histogram such that, for standard energy deposition histograms, 
		the "y" values are the cross section for generating a given amount of energy or greater. '''
		return self.df[['y', 'y2']][::-1].cumsum()[::-1]
		#self.df[['y', 'y2']] = self.df[['y', 'y2']][::-1].cumsum()[::-1]
		#return df

	def getTotalDose(self, includeUnderflowBin=False):
		startIndex = 0 if includeUnderflowBin else 1
		return np.sum(list(self.df['x'] * self.df['y'])[startIndex:])
	

####################
# \class Hdf5Data
class Hdf5Data(_NameMgr):
	'''	Hdf5Data class. Provides methods for intelligently loading large hdf5 files from MRED
	If no file name is given, the class looks to the options parser, then finally to whichever *.hdf5 
 	file happens to be loaded first in the working directory (also selectable via command line flag)'''
	def __init__(self, filename=None, histogramNames=[], exact=False, getHistograms=options.load):

		self.filename = filename if filename else options.files 
		self.filename = self.filename if self.filename else [options.directory + '/' + x for x in os.listdir(options.directory) if '.hdf5' in x][0]
		self.loadedHistograms =[] 
		self.histogramDict = {}
		self.__nameMap = {}
		self.attrs = {}

		with hp.File(self.filename,'r' ) as f:
			tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
			self.__stringData = [x[0] for x in tables['string_data'][()]]
			self.__strings = tables['strings'][()]
			self.__histograms = tables['histograms'][()]
			for key in f.attrs.keys():
				self.attrs[key] = f.attrs[key]
			self.__constructNameMap()
			super().__init__(list(self.__nameMap.keys()))
			if histogramNames:
				self.selectNames(histogramNames)
			if getHistograms:
				self.getHistograms()
	
	def __repr__(self):
		return "Hdf5Data Object for file: {}".format(self.filename)
	
	def resetHistograms(self):
		''' Clears the histogram list'''
		for h in self.loadedHistograms:
			del h
		for h,v in self.histogramDict.items():
			del v
		self.histogramDict = {}
		self.loadedHistograms=[]

	def __getHistogramName(self, strings):
		''' Converts the ascii stringData array to histogram names	
		@strings is a tuple as given by the strings attribute of the hdf5 table. 
		E.g. tables['strings'] --> [(0, 1), (1, 5), (6, 3), ...] where the first index points to the 
		start of the string in stringData, and the second is the legnth '''
		startIndex = strings[0]
		stringLength = strings[1] - 1
		histogramName = ''.join([chr(self.__stringData[startIndex+x]) for x in range(stringLength)])
		return histogramName

	def __constructNameMap(self):
		try:
			for i in self.__histograms:
				histogramName = self.__getHistogramName(self.__strings[i[0]])
				self.__nameMap[histogramName] = (i[1], i[1]+i[2])
		except Exception as e:
			print("Error in Hdf5Data.__constructNameMap() ")
			print(e)

	def __getNormFactor(self, nIonsAttr='nIons', gfuAttr='gfu'):
		'''	Returns the normalization factor by looking for the HDF5 file attributes
		"nIons" and "gfu" (by default). Normalization factor is given by 1 / (gfu * nIons). '''
		try:
			if not options.raw:
				return 1./(self.attrs[nIonsAttr][0] * self.attrs[gfuAttr][0])
		except Exception as e:
			print("Error in __getNormFactor()")
			print(e)
			try:
				return 1./(self.attrs[nIonsAttr][0])
			except:
				print("couldn't normalize by ions")
		return 1

	def printAttributes(self, attribute='all'):
		'''	Prints the file attributes of the HDF5 file (entered at runtime in MRED). Lists all of the attribute names
			and values by default, or only the attribute passed as a function argument'''
		filename = self.filename.split("/")[-1] if "/" in self.filename else self.filename
		print(f"{filename}")
		for a in list(self.attrs.items()):
			for attribute in attribute:
				if attribute in a[0] or attribute=='all':
					try:
						print("\t{:<15}\t{:<15}".format(str(a[0]), str(a[1])))
						break
					except:
						print("ERROR: with printing the attribute(s) for {}".format(self.filename))

	def _getHistogram(self, histName=None, diff = ""):
		'''	returns only one histogram labelled by @histName for a given file. Defaults to the first histogram if no 
		@histName passed. If options.diff is set to True, the data is given with only the fluence normalization applied; 
		if set to False, the reverse integrated cross section is given. '''
		diff = diff if diff else options.diff
		try:
			histName = histName if histName else self.names[0]
			print("histogram name: {}".format(histName))

			if histName in self.histogramDict.keys():
				return self.histogramDict[histName]

			with hp.File(self.filename, 'r') as f:
				tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
				df = pd.DataFrame(tables['histogram_data'][()][ self.__nameMap[histName][0] : self.__nameMap[histName][1] ])
			df.name = self.filename + " - " +histName
			df[['y', 'y2']] *= self.__getNormFactor()
			histogram = Histogram(df = df, histname=histName, filename = self.filename)

			if not diff:
				histogram.df = histogram.revInt()
			#self.loadedHistograms.append(histogram)
			#self.histogramDict[histName] = histogram
			return histogram
		except Exception as e:
			print("Error in _getHistogram() method: ")
			print(e)
	 
	def getHistograms(self, histogramNames=None):
		'''	returns a dictionary of histogram DataFrames with the names as keys for the histogram names passed 
		as a list. 
	 	Defaults behavior is to return all histogramNames within a given hdf5 file. '''
		output=[]
		histogramNames = histogramNames if histogramNames else self.names[0]#only load the first one? have an option flag set for this? 
		try:
			for histName, histBounds in self.__nameMap.items():
				if histName in histogramNames:
					histogram = self._getHistogram(histName)
					output.append(histogram)
			return output
		except Exception as e:
			print("Error in getHistograms() method. ")
			print(e)
	 
	# pass a list of histogram objects here instead of the histogram names? 
	def plot(self, histograms=None, histogramNames=None, log=True, xlim=(1e-3, 1e2), ylim=(1e-20,1e-4), title="", save=False):
		plt.figure()
		ax = plt.subplot()
		histograms = histograms if histograms else self.getHistograms(histogramNames)
		for histogram in histograms:
			df = histogram.df
			if histogram.color:
				df.plot(x='x', y='y', logx=log, logy=True, xlim=xlim, ylim=ylim, label=histogram.label, ax=ax, color=color)
			else:
				df.plot(x='x', y='y', logx=log, logy=True, xlim=xlim, ylim=ylim, label=histogram.label, ax=ax)
		ax.set_xlabel("Energy Deposited [MeV]")
		#plt.set_ylabel("Energy Deposited [MeV]")
		ax.set_title(title)
		return ax
#		plt.show()

####################
# \class Hdf5Files
class Hdf5Files:
	def __init__(self, files=[]):
		'''Sets the current files attribute to the list explicitly passed, or the list passed via the
		options parser, or finally all HDF5 files in the directory, in that order		'''
		if files:
			self.__names = files
		elif options.files:
			self.__names = options.files
		else:
			files = [options.directory + x for x in os.listdir(options.directory) if '.hdf5' in x]
			self.__names = files
		self.__loadedHistograms = []
		self.__loadedDict = {}
		self.histNames = self.__getAllHistogramNames()
		self._reset = self.histNames

	def __repr__(self):
		return "\nfiles current loaded in Hdf5Files object: \n{}\n-----------------------------\n".format(str(self.__names))
	
	def __getAllHistogramNames(self):
		hists = []
		for name in self.__names:
			data = Hdf5Data(name)
			for histogram in data.names:
				hists.append(name + " / " + histogram)
		return hists

	# pass a list of histogram objects here instead of the histogram names? 
	def plotAll(self, log=True, xlim=(1e-3, 1e2), ylim=(1e-20,1e-4), title="", save=False):
		plt.figure()
		ax = plt.subplot()
		self.__loadHistograms()
		histograms = self.__loadedHistograms
		for histogram in histograms:
			df = histogram.df
			if histogram.color:
				df.plot(x='x', y='y', logx=log, logy=True, xlim=xlim, ylim=ylim, label=histogram.label, ax=ax, color=color)
			else:
				df.plot(x='x', y='y', logx=log, logy=True, xlim=xlim, ylim=ylim, label=histogram.label, ax=ax)
		ax.set_xlabel("Energy Deposited [MeV]")
		#plt.set_ylabel("Energy Deposited [MeV]")
		ax.set_title(title)
		plt.show()

	#def resetLoadedHistograms(self):
	#	''' Clears the histogram list'''
	#	for h in self.loadedHistograms:
	#		del h
	#	self.loadedHistograms=[]

	def __loadHistograms(self, filename=None):
		try:
			for fh in self.histNames:
				if fh in self.__loadedDict.keys():
					pass
				else:
					filename, histname = fh.split(" / ")
					histogram = Hdf5Data(filename, histname)._getHistogram(histname)
					self.__loadedHistograms.append(histogram)
					self.__loadedDict[fh] = histogram
		except Exception as e:
			print("Error in getHistograms() method. ")
			print(e)

	#listFiles = property(lambda self: self._listFiles(), lambda self, attributes: self._listFiles(self, attributes), None, "")
	def showFiles(self, attributes='',allFiles=False):
		'''Lists the names files in one column for easier reading. If a file attribute (set at run time in MRED) 
		is passed, the value of that attribute for each file is also presented. set @attribute = 'all' to return all 
		HDF5 file attributes associated with each file.'''
		dirs = self.__names if allFiles else set([x.split(" / ")[0] for x in self.histNames])
		if attributes:
			for f in dirs:
				Hdf5Data(f).printAttributes(attribute=attributes)
		else:
			print('\n'.join(dirs))
	
	def showHistograms(self):
		dirs = set([x.split(" / ")[0] for x in self.histNames])
		for parent in dirs:
			print("--------------------------------------------")
			print(parent)
			for hist in self.histNames:
				if parent in hist:
					print("  +-- {}".format(hist.split(" / ")[1]))

	def dropHistograms(self, dropFilters, exact = False):
		'''Updates the names file list, droppinng files which match the filterString(s).'''
		if type(dropFilters) == list:
			for dropFilter in dropFilters:
				self.dropHistograms(dropFilter, exact = exact)
		else:
			if exact:
				selected = [f for f in self.histNames if dropFilters != f]
			else:
				selected = [f for f in self.histNames if dropFilters not in f]
			self.histNames = selected

	def selectHistograms(self, selectFilters, exact = False):
		'''Updates the names file list to only include those file(s) which match the filterString(s)'''
		if type(selectFilters) == list:
			for selectFilter in selectFilters:
				self.selectHistograms(selectFilter, exact = exact)
		else:
			if exact:
				selected = [f for f in self.histNames if selectFilters == f]
			else:
				selected =  [f for f in self.histNames if selectFilters in f]
			self.histNames = selected

	def resetHistograms(self):
		self.histNames = self._reset


files = Hdf5Files()
