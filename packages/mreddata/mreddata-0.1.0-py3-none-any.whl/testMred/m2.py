import h5py as hp
import numpy as np
import pandas as pd
import argparse, sys, os
import matplotlib.pyplot as plt 

def resetOptions():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--files' , type=str, nargs="+", default=[], help='Only load data from the HDF5 files listed after this flag (rather than every HDF5 in the directory)')
	parser.add_argument('--raw', action='store_true', default=False, help='only return the raw data, with no normalization - post processing applied (default is normalized the gun fluence unit and nIons)')
	parser.add_argument('--diff', action='store_true', default=False, help='differntial data (default is reverse-integrated)')
	parser.add_argument('--fullpath', '--includeFilenames', action='store_true', default=False, help='include the full filename')
	parser.add_argument('-x', '--no-load', action='store_true', default=False, help='Only load the file/histogram names into memory, not the histogram data. Usefull for files with a large number of histograms')
	options, __remaining = parser.parse_known_args(sys.argv[1:])
	if not options.files:
		from glob import glob
		options.files = glob("*.hdf5")
	return options

options = resetOptions()

######################
class Histogram:
	def __init__(self, df, histname, filename, label=None, color=None):
		self.df = df
		self.filename = filename
		self.name = histname
		self.label = label 
		self.color = color
		self.fullpath = self.filename + " - " + self.name

	def __repr__(self):
		if options.fullpath:
			return self.filename + " - " + self.name
		else:
			return self.name
	
	def revInt(self):
		try:
			return self.df[['y','y2']][::-1].cumsum()[::-1]
		except:
			print("ERROR -- no data in Histogrm object")


	def totalDose(self):
		try:
			return np.sum(list(self.df['x'] * self.df['y'])[1:-1])
		except:
			print("ERROR -- no data in Histogrm object")

######################
class _HistogramListMgr:
	def __init__(self, listIn = []):
		self.histograms = []
		if type(listIn[0]) == str:
			for item in listIn:
				if " - " not in item:
						
					print("\n\n\n***********************\nERROR in setting Histogram object list. If only entering names and not Histogram objects, these should be in the format of '/path/to/filename.hdf5 - histogramName' (i.e. with a space-slash-space separating the filename and histogram name).\n\nBreaking from this entry. {}\n\n".format(item))
					break
				else:
					filename, histname = item.split(" - ")
					self.histograms.append(Histogram(df=None, histname=histname, filename=filename))
		else:
			self.histograms = listIn
		self._reset = self.histograms
		self.histogramsDict ={} 
		for item in self.histograms:
			self.histogramsDict[item.fullpath] = item

	histNames = property(lambda self: [x.fullpath if options.fullpath else x.name for x in self.histograms if type(x) == Histogram], None, None, "")

	def __repr__(self):
		#return "\n--------------------------------\ncurrent histograms in list:\n{}\n-------------------------------".format(str(self.histNames))
		self.displayHistograms()
		return ""

	def dropHistograms(self, *args, exact=False, dropFilter=None):
		if args:
			for item in args:
				if type(item) == list:
					for i in item:
						self.dropHistograms(exact=exact, dropFilter=i)
				else:
					self.dropHistograms(exact=exact, dropFilter=item)
		else:
			if exact:
				selected = [f for f in self.histograms if dropFilter != f.name]
			else:
				selected = [f for f in self.histograms if dropFilter not in f.fullpath]
			self.histograms = selected

	def selectHistograms(self, *args, exact=False, selectFilter=None):
		if args:
			for item in args:
				if type(item) == list:
					for i in item:
						self.selectHistograms(exact=exact, selectFilter=i)
				else:
					self.selectHistograms(exact=exact, selectFilter=item)
		else:
			if exact:
				selected = [f for f in self.histograms if selectFilter == f.name]
			else:
				selected = [f for f in self.histograms if selectFilter in f.fullpath]
			self.histograms = selected

	def resetHistograms(self):
		self.histograms = self._reset
	
	def displayHistograms(self):
		dirs = set([x.filename for x in self.histograms])
		for parent in dirs:
			print("---------------------------------------")
			print(parent)
			for hist in self.histograms:
				if parent in hist.filename:
					print(" +-- {}".format(hist.name))
		# have method to delete the data? reduce memory load? 
	#showHistograms = property(lambda self: self._displayHistograms(), None, None, "")

######################
class Hdf5Data(_HistogramListMgr):
#class Hdf5Data:

	def __init__(self, filename, histogramNames=[]):

		self.filename = filename if filename else options.files[0]	
		self.__nameMap = {}
		self.attrs = {}

		try:
			with hp.File(self.filename, 'r') as f:
				tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
				self.__stringData = [x[0] for x in tables['string_data'][()]] 
				self.__strings = tables['strings'][()]
				self.__histograms = tables['histograms'][()]
				for key in f.attrs.keys():	# populate the attributes dict
					self.attrs[key] = f.attrs[key]
			self.__constructNameMap()
			super().__init__([self.filename + " - " + x for x in list(self.__nameMap.keys())])
			#self.histograms = _HistogramListMgr([self.filename + " - " + x for x in list(self.__nameMap.keys())])

		except Exception as e:
			print("ERROR creating Hdf5Data object for {}".format(self.filename))
			print(e)
			return False
	
	def __getHistogramName(self, strings):
		return ''.join([chr(self.__stringData[strings[0]+x]) for x in range(strings[1]-1)])
	def __constructNameMap(self):
		for i in self.__histograms:
			histogramName = self.__getHistogramName(self.__strings[i[0]])
			self.__nameMap[histogramName] = (i[1], i[1]+i[2])
	def __getNormFactor(self, nIonsAttr='nIons', gfuAttr='gfu'):
		try:
			if not options.raw:
				return 1./(self.attrs[nIonsAttr][0] * self.attrs[gfuAttr][0])
		except Exception as e:
			print("Error in __getNormFactor: {}".format(e))
			try:
				return 1./self.attrs[nIonsAttr][0]
			except:
				print("couldn't normalize by ions...returning 1")
				return 1
	
	def _getHistogram(self, histogramName=None, diff=None):
		diff = diff if diff else options.diff
		try:
			displaystate = options.fullpath
			options.fullpath = True
			histogramName = histogramName if histogramName else self.histNames[0].split(" - ")[1]
			options.fullpath = displaystate
			print('histogram name loaded as : {}'.format(histogramName))
			with hp.File(self.filename, 'r') as f:
				tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
				df = pd.DataFrame(tables['histogram_data'][()][self.__nameMap[histogramName][0] : self.__nameMap[histogramName][1]])
				print("Successfully loaded df")
			df.name = self.filename + " - " + histogramName
			df[['y', 'y2']] *= self.__getNormFactor()

			histogram = self.histogramsDict[df.name]#Histogram(df=df, histname=histogramName, filename = self.filename)
			histogram.df = df

			if not diff:
				histogram.df = histogram.revInt()
			return histogram
		except Exception as e:
			print("ERROR in _getHistogram method: {}".format(e))
			
	def getHistograms(self, histogramNames=None):
		output=[]
		displaystate = options.fullpath
		options.fullpath = True
		histogramNames = histogramNames if histogramNames else [x.split(" - ")[1] for x in self.histNames]
		options.fullpath = displaystate
		try:
			for histName, histBounds in self.__nameMap.items():
				if histName in histogramNames:
					if " - " in histName:
						histName = histName.split(" - ")[1]
					histogram = self._getHistogram(histName)
					output.append(histogram)
			return output
		except Exception as e:
			print("ERROR in getHistograms method: {}".format(e))


class Hdf5Files(Hdf5Data):
	def __init__(self):
		#self.data = []	
		#self.data = [Hdf5Data(f) for f in options.files]
		for f in options.files:
			super().__init__(f)

#files = FilesManager()

		#	histogramName = histogramName if histogramName else self.histograms.	
			# have two different kinds of histogram name manager objects, one for histogram objects and another for the names? 
# or only one with the default being that histograms are loaded into memory, with hidden methods for loading manually in the case of not automatically loading into memory
