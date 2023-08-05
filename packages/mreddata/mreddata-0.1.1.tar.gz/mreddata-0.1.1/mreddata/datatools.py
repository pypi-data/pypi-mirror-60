import h5py as hp
import numpy as np
import pandas as pd
import argparse, sys, os
import matplotlib.pyplot as plt 
 
class PlotOptions:
	def __init__(self, dictIn=None):
		if dictIn:
			self.__dict__.update(dictIn)	
		else:
			self.resetDefaults()
	
	def resetDefaults(self):
		self.fontsize = 10
		self.xlim = (1e-3, 1e2)
		self.ylim = (1e-20, 1e-5)
		self.dpi = 100
		self.title = ""
		self.xlabel = "Energy Deposited [MeV]"
		self.ylabel = ""
		self.logx = True
		self.logy = True
		self.size = (6.4, 4.8)
		self.legendPadding = 0.8
		self.save = False
		self.saveOnly = False 				# Don't plot, just save 
		self.saveFormat = 'png'
		self.saveName = ''
		self.bbox_inches = 'tight'			# fits legend when saving plot 
		self.legend = None 					# default to file/histogram names
		self.loc = 'center left'			# legend location
		self.bbox_to_anchor = (1.05, 0.5) 	# legend anchor 

plot_options = PlotOptions()

def resetOptions():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--files' , type=str, nargs="+", default=[], help='Only load data from the HDF5 files listed after this flag (rather than every HDF5 in the directory)')
	parser.add_argument('--raw', action='store_true', default=False, help='only return the raw data, with no normalization - post processing applied (by default, data is normalized to the gun fluence unit and nIons)')
	parser.add_argument('--diff', action='store_true', default=False, help='differntial data (default is reverse-integrated)')
	parser.add_argument('--fullpath', '--includeFilenames', action='store_true', default=False, help='include the full filename')
	parser.add_argument('-x', '--no-load', action='store_true', default=False, help='Only load the file/histogram names into memory, not the histogram data. Usefull for files with a large number of histograms')
	parser.add_argument('-e', '--include-error', action='store_true', default=False, help='include error bars in the plot')
	options, __remaining = parser.parse_known_args(sys.argv[1:])
	if not options.files:
		from glob import glob
		options.files = glob("*.hdf5")
	return options

options = resetOptions()

######################
# \class Histogram
class Histogram:
	def __init__(self, histname, filename, df = None, label=None, color=None):
		self.df = df
		self.filename = filename
		self.name = histname
		self.color = color
		self.fullpath = self.filename + " - " + self.name
		self.label = self.fullpath 
		self.totalDose = 0
		self.sortOrder = None

	def __repr__(self):
		if options.fullpath:
			return self.filename + " - " + self.name
		else:
			return self.name
	
	def revInt(self, update=False):
		''' Integrates the event count over energy deposition bins from high energy to low energy. When properly normalized, 
		this gives the cross section for depositing energy above a certain threshold. Default behavior is to only return the 
		integrated histogram, but if the update parameter is set to true, the dataframe of the histogram object will be updated.'''
		try:
			oldDf = self.df.loc[:]
			dff = self.df.loc[:, ('y', 'y2')][::-1].cumsum()[::-1]
			oldDf.update(dff)
			self.df = oldDf
			del oldDf, dff
		except:
			print("ERROR -- no data in Histogram object")


	def totalDose(self):
		''' Returns the total dose accumulated in a sensitive region's histogram. Does not include the under/overflow bins. 
		Default MRED units assumed -- MeV '''# TODO: Include conversion to useful units ( rad (SiO2) )
		print("DELTE total dose function called. ")
		try:
			self.totalDose =  np.sum(list(self.df['x'] * self.df['y'])[1:-1])
			return self.totalDose
		except:
			print("ERROR -- no data in Histogram object")
	
	def normalize(self, normalizationFactor):
		dff =self.df.loc[:, ('y', 'y2')].apply(lambda x: x/normalizationFactor)
		oldDf = self.df.loc[:]
		oldDf.update(dff)
		self.df = oldDf
		del oldDf, dff
	
	def binWidthScale(self):
		dff = (self.df.loc[:, ('y', 'y2')].T / self.df.loc[:, ('w')]).T
		oldDf = self.df.loc[:]
		oldDf.update(dff)
		self.df = oldDf
		del oldDf, dff

######################
# \class _HistogramListMgr
#	
#	This private class provides utilities for managing the histogram object list such as sorting, selecting, filtering
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
					self.histograms.append(Histogram(histname=histname, filename=filename))
		else:
			self.histograms = listIn
		self._reset = self.histograms
		self.histogramsDict ={} 
		for item in self.histograms:
			self.histogramsDict[item.fullpath] = item
		self.customHistograms = []

	_histNames = property(lambda self: [x.fullpath if options.fullpath else x.name for x in self.histograms if type(x) == Histogram], None, None, "")


	def __repr__(self):
		self.displayHistograms()
		return ""

	def dropHistograms(self, *args, exact=False, dropFilter=None):
		''' Removes histograms from the list based on any number of matching strings passed as arguments. '''
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
		''' Updates the histogram object list to only include those histograms which match the patterns passed as string arguments'''
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
		''' update the histogram list to its original (complete) state'''
		self.histograms = self._reset
	
	def displayHistograms(self):
		''' Displays the directory tree of histograms/files in the histogram object list'''
		dirs = set([x.filename for x in self.histograms])
		for parent in dirs:
			print("---------------------------------------")
			print(parent)
			print("  |")
			for hist in self.histograms:
				if parent in hist.filename:
					print(" +-- {}".format(hist.name))

	def combineHistograms(self, newHistName, label="", color="", histograms=[]):
		#TODO: add different method to join the combine and select methods? i.e. pass a string of arguments to filter the default Histogram object list, and then combine those. Not sure if this is necessary. 
		#TODO: add method for saving to file
		''' Combines all of the histgorams in the current Histogram object list''' 
		if not histograms:
			histograms = self.histograms
		newHist = Histogram(histname = newHistName , filename='combined histograms', label=label, color=color)
		newHist.df = self.histograms[0].df.loc[:, ('x', 'w', 'edges')]
		for h in histograms:
			if (h.df[['x', 'w', 'edges']] == newHist.df[['x', 'w', 'edges']]).all().all():#check that bins match
				if 'y' in newHist.df.columns:
					newHist.df[['y', 'y2', 'xy', 'x2y', 'n']] += h.df.loc[:, ('y', 'y2', 'xy', 'x2y', 'n')] 
				else:
					newHist.df[['y', 'y2', 'xy', 'x2y', 'n']] = h.df.loc[:, ('y', 'y2', 'xy', 'x2y', 'n')]
			else:
				print("ERROR: Cannot combine historams because the bins do not match. (failed on histogram: {})".format(h))
				#TODO: add method for combining histograms with different bins
		newHist.df = newHist.df[['x', 'y', 'y2', 'xy', 'x2y', 'n', 'w', 'edges']]
		self.customHistograms.append(newHist)
			
		
######################
# \class Hdf5Data
#
# 	The main datatool object in mreddata, providing data manipulation and plotting methods. 
class Hdf5Data(_HistogramListMgr):

	def __init__(self):

		self.__nameMap = {}
		self.__attrs = {} 
		self.__stringData = {}
		self.__strings = {}
		self.__histograms = {}

		for filename in options.files:
			try:
				with hp.File(filename, 'r') as f:
					tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
					self.__stringData[filename] = [x[0] for x in tables['string_data'][()]] 
					self.__strings[filename] = tables['strings'][()]
					self.__histograms[filename] = tables['histograms'][()]
					self.__attrs[filename] = {}
					for key in f.attrs.keys():	# populate the attributes dict
						self.__attrs[filename][key] = f.attrs[key]
				self.__constructNameMap(filename)

			except Exception as e:
				print("ERROR creating Hdf5Data object for {}".format(filename))
				print(e)

		#  this is a 1-D dictionary as opposed to the other private attributes
		try:
			super().__init__(list(self.__nameMap.keys()))
		except:
			print("ERROR: Couldn't load histgrams...check the path to make sure it's where the Hdf5 files are located40k.")
		if not options.no_load: 			#	--no-load is usefull for large files with many histograms; allows exploration of available options without loading into memory
			self.__loadAllHistograms()


	def __getHistogramName(self, strings, filename):
		return ''.join([chr(self.__stringData[filename][strings[0]+x]) for x in range(strings[1]-1)])
	def __constructNameMap(self, filename):
		for i in self.__histograms[filename]:
			histogramName = self.__getHistogramName(self.__strings[filename][i[0]], filename)
			self.__nameMap[filename + " - " + histogramName] = (i[1], i[1]+i[2])
	def __getNormFactor(self, filename, nIonsAttr='nIons', gfuAttr='gfu'):
		try:
			if not options.raw:
				nf =  self.__attrs[filename][nIonsAttr][0] * self.__attrs[filename][gfuAttr][0]
				return nf
		except Exception as e:
			print("Error in __getNormFactor: {}".format(e))
			try:
				return self.__attrs[filename][nIonsAttr][0]
			except:
				print("couldn't normalize by ions...returning 1")
				return 1


	def attributes(self, *args):
		''' Displays the file attributes for all files in the current Histogram object list. Shows all file attributes by default, 
		with the options to pass strings as arguments to view only those attribuetes. '''
		for filename, attributeKeys in self.__attrs.items():
			print("--------------------------------")
			print(f"{filename}")
			print("  |")
			for k, a in attributeKeys.items():
				if args:
					for arg in args:
						if arg in k:
							print("  +-- {:<15}\t{:<15}".format(str(k), str(a)))
				else:
					print("  +-- {:<15}\t{:<15}".format(str(k), str(a)))

	
	def _getHistogram(self, filename,  histogramName=None, diff=None):
		''' Loads a histogram from the given @filename. Defaults to the first histgoram in the file, but can select 
		which histogram to load with @histogramName'''
		diff = diff if diff else options.diff
		try:
			displaystate = options.fullpath
			options.fullpath = True
			histogramName = histogramName if histogramName else self._histNames[0]
			options.fullpath = displaystate
			try:
				if self.histogramsDict[filename + " - " + histogramName].df:
					return self.histogramsDict[filename + " - " + histogramName]
			except:
				pass
			with hp.File(filename, 'r') as f:
				tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
				df = pd.DataFrame(tables['histogram_data'][()][self.__nameMap[filename + " - " + histogramName][0] : self.__nameMap[filename + " - " + histogramName][1]])
			df.name = filename + " - " + histogramName
			histogram = self.histogramsDict[df.name]
			histogram.df = df
			histogram.normalize(self.__getNormFactor(filename=filename))
			if not options.diff:
				histogram.df = histogram.revInt()
			else:
				if not options.raw:
					histogram.df = histogram.binWidthScale()
			return histogram
		except Exception as e:
			print("ERROR in _getHistogram method: {}".format(e))
			
	def getHistograms(self, filename=None, histogramNames=None):
		''' Load and return all of the histograms in the current Histogram object list.'''
		output=[]
		filenames = [x.filename for x in self.histograms]
		try:
			displaystate = options.fullpath
			options.fullpath = True
			for filename in filenames:
				histogramNames = [x for x in self._histNames if filename in x]
				for histName, histBounds in self.__nameMap.items():
					if filename in histName:
						if histName in histogramNames:
							if " - " in histName:
								histName = histName.split(" - ")[1]
							histogram = self._getHistogram(filename = filename, histogramName=histName)
							output.append(histogram)
			options.fullpath = displaystate
			return output
		except Exception as e:
			options.fullpath = displaystate
			print("ERROR in getHistograms method: {}".format(e))
	
	def __loadAllHistograms(self):
		if not options.no_load:
			for filename in options.files:
				with hp.File(filename, 'r') as f:
					normFactor = self.__getNormFactor(filename=filename)
					tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
					file_df = pd.DataFrame(tables['histogram_data'][()])
					for key, bounds in self.__nameMap.items():
						if filename in key:
							histogram = self.histogramsDict[key]
							histogram.df = file_df.loc[bounds[0]:bounds[1]-1].reset_index(drop=True)
							histogram.normalize(normFactor)
							if not options.diff:
								histogram.revInt()
				del tables, file_df

	def plot(self, histograms = [], **kwargs):
		# override global plot_options in this instance with kwargs passed as function parameters; set kwargs specific to df.plot()
		allOptions = PlotOptions(plot_options.__dict__)
		allOptions.__dict__.update(kwargs)
		plotKwargs = {k:v for k, v in allOptions.__dict__.items() if k in ['kind', 'figsize', 'use_index', 'title', 'grid', 'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'colorbar', 'position', 'table', 'yerr', 'xerr']}

		# load histograms
		if not histograms:
			histograms = self.histograms

		plt.figure()
		ax = plt.subplot()

		for histogram in histograms:
			df = histogram.df
			if histogram.color:
				df.plot(x='x', y='y', label = histogram.label, color=color, ax = ax, **plotKwargs)
			else:
				df.plot(x='x', y='y', label = histogram.label, ax = ax, **plotKwargs)

		if allOptions.legend:
			ax.legend(allOptions.legend, loc=allOptions.loc, bbox_to_anchor = allOptions.bbox_to_anchor)
		else:
			ax.legend(loc=allOptions.loc, bbox_to_anchor = allOptions.bbox_to_anchor)
		ax.set_xlabel(allOptions.xlabel)
		ax.set_ylabel(allOptions.ylabel)
		ax.set_title(allOptions.title)
		plt.subplots_adjust(right=allOptions.legendPadding)

		# Saves based on saveName option setting, or title if none, or defaultSaveName if no title.
		if allOptions.save:
			if not allOptions.saveName:
				if not allOptions.title:
					allOptions.saveName = 'defaultSaveName'
				else:
					allOptions.saveName = allOptions.title
			plt.savefig(allOptions.saveName+"."+allOptions.saveFormat, format=allOptions.saveFormat, dpi=allOptions.dpi, bbox_inches=allOptions.bbox_inches)

		if not allOptions.saveOnly:
			plt.show()

mreddata = Hdf5Data()
