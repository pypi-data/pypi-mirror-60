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
		self.ylim = 'auto'#(1e-20, 1e-5)
		self.dpi = 100
		self.title = ""
		self.xlabel = "Energy Deposited [MeV]"
		self.ylabel = ""
		self.logx = True
		self.logy = True
		self.size = (6.4, 4.8)
		self.dashes = (None, None)
		self.dashesOn = True
		self.drawstyle = 'steps' # or default
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
	parser.add_argument('--diff', action='store_true', default=False, help='differntial data (default is reverse-integrated; selecting this normalizes histogram data and scales by bin-width)')
	parser.add_argument('--fullpath', '--includeFilenames', action='store_true', default=False, help='include the full filename')
	parser.add_argument('--no-load', action='store_true', default=False, help='Only load the file/histogram names into memory, not the histogram data. Usefull for files with a large number of histograms')
	parser.add_argument('--no-norm', action='store_true', default=False, help='for pkl/txt files; selecting this flag disables the interactive setting of the gfu and nIons for the run/file.')
	parser.add_argument('-m', '--manual-load', action='store_true', default=False, help='default behavior for mreddata is to autodetect what kind of file is being opened. Use the manual flag to select the data type class (Hdf5Data(), PklData(), TxtData()) manually. The default selection is based on the file extensions of whichever file is first in options.files, and renders the appropriate class as Data() (e.g. using "import Hdf5Data as Data")')
	#parser.add_argument('-e', '--include-error', action='store_true', default=False, help='include error bars in the plot')TODO
	options, __remaining = parser.parse_known_args(sys.argv[1:])
	if not options.files:
		from glob import glob
		options.files = glob("*.hdf5")
		if not options.files:
			options.files = glob("*.pkl")
			if not options.files:
				options.files = glob("*.txt")
	return options

options = resetOptions()

######################
# \class Histogram
class Histogram:
	def __init__(self, histname, filename, df = None, label=None, color=None, dashes = (None, None), sortOrder=None):
		self.df = df
		self.filename = filename
		self.name = histname
		self.color = color
		self.fullpath = self.filename + " - " + self.name
		self.label = self.fullpath 
		self.totalDose = 0
		self.sortOrder = sortOrder
		self.normFactor = 1
		self.dashes = dashes

	def __repr__(self):
		if options.fullpath:
			return self.filename + " - " + self.name
		else:
			return self.name
	
	def revInt(self):#, update=False):
		''' Integrates the event count over energy deposition bins from high energy to low energy. When properly normalized, 
		this gives the cross section for depositing energy above a certain threshold. Default behavior is to only return the 
		integrated histogram, but if the update parameter is set to true, the dataframe of the histogram object will be updated.'''
		try:
			oldDf = self.df.loc[:]
			dff = self.df.loc[:, ('y', 'y2')][::-1].cumsum()[::-1]
			dff.columns = ['y', 'y2']
			oldDf.update(dff)
			self.df = oldDf
			del oldDf, dff
		except:
			print("ERROR -- no data in Histogram object")

	
	def getHistAtE(self, energy, column = None):
		idx = np.abs(self.df['x'] - energy).idxmin()		
		if column:
			return list(self.df[idx:idx + 1][column])[0]
		else:
			return self.df[idx:idx + 1]

	def getTotalDose(self):####Need way of converting from revInt back to diff/raw for calculating total dose. 
		''' Returns the total dose accumulated in a sensitive region's histogram. Does not include the under/overflow bins. 
		Default MRED units assumed -- MeV '''# TODO: Include conversion to useful units ( rad (SiO2) )
		try:
			self.totalDose =  np.sum(list(self.df['x'] * self.df['y'])[1:-1])
			return self.totalDose
		except:
			print("ERROR -- no data in Histogram object")
	
	def normalize(self):#, normFactor):
		#if self.normFactor != normFactor:
		#	self.normFactor = normFactor
		dff =self.df.loc[:, ('y', 'y2')].apply(lambda x: x/self.normFactor)
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
class _HistogramList:
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
					print("  ├── {}".format(hist.name))

	def combineHistograms(self, newHistName, label="", color="", histograms=[]):
		#TODO: add different method to join the combine and select methods? i.e. pass a string of arguments to filter the default Histogram object list, and then combine those. Not sure if this is necessary. 
		#TODO: add method for saving to file
		''' Combines all of the histgorams in the current Histogram object list''' 
		if not histograms:
			histograms = self.histograms
		newHist = Histogram(histname = newHistName , filename='combined histograms', label=label, color=color)
		newHist.df = self.histograms[0].df.loc[:, ('x', 'w', 'edges')]
		for h in histograms:
			if (h.df[:len(h.df) - 1][['x', 'w', 'edges']] == newHist.df[:len(newHist.df) - 1][['x', 'w', 'edges']]).all().all():#check that bins match; don't include overflow (null value in edges causes check to fail)
				if 'y' in newHist.df.columns:
					newHist.df[['y', 'y2', 'xy', 'x2y', 'n']] += h.df.loc[:, ('y', 'y2', 'xy', 'x2y', 'n')] 
				else:
					newHist.df[['y', 'y2', 'xy', 'x2y', 'n']] = h.df.loc[:, ('y', 'y2', 'xy', 'x2y', 'n')]
			else:
				print("ERROR: Cannot combine historams because the bins do not match. (failed on histogram: {})".format(h))
				#TODO: add method for combining histograms with different bins
		#newHist.df = newHist.df[['x', 'y', 'y2', 'xy', 'x2y', 'n', 'w', 'edges']]
		self.customHistograms.append(newHist)
			

	#TODO: Auto-determine plot limits based on the data. Toggle this as an option
	def plot(self, histograms = [], **kwargs):
		# override global plot_options in this instance with kwargs passed as function parameters; set kwargs specific to df.plot()
		allOptions = PlotOptions(plot_options.__dict__)
		allOptions.__dict__.update(kwargs)
		plotKwargs = {k:v for k, v in allOptions.__dict__.items() if k in ['kind', 'figsize', 'use_index', 'title', 'grid', 'legend', 'style', 'logx', 'logy', 'loglog', 'xticks', 'yticks', 'xlim', 'ylim', 'rot', 'fontsize', 'colormap', 'colorbar', 'position', 'table', 'yerr', 'xerr', 'dahses', 'drawstyle']}

		# load histograms
		if not histograms:
			histograms = self.histograms
		if allOptions.ylim == 'auto':
			yMin = 1e300
			yMax = 1e-300
			for h in histograms:
				tmin = h.df[h.df['y'] > 0]['y'].min()
				tmax = h.df[h.df['y'] > 0]['y'].max()
				yMin = tmin if tmin < yMin else yMin
				yMax = tmax if tmax > yMax else yMax
			yMax *= 10
			allOptions.ylim = (yMin, yMax)

		plt.figure()
		ax = plt.subplot()

		for histogram in histograms:
			df = histogram.df
			if allOptions.dashesOn:
				if histogram.color:
					df.plot(x='x', y='y', label = histogram.label, dashes = histogram.dashes, color=histogram.color, ax = ax, **plotKwargs)
				else:
					df.plot(x='x', y='y', label = histogram.label, dashes = histogram.dashes, ax = ax, **plotKwargs)
			else:
				if histogram.color:
					df.plot(x='x', y='y', label = histogram.label, color=histogram.color, ax = ax, **plotKwargs)
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
