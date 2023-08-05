#!/usr/bin/python
__all__ = ['Hdf5Data']
import os
import numpy as np
import h5py as hp
import pandas as pd
from ._options_parser import options

class Hdf5Data:
	'''
 	Hdf5Data class. Provides methods for intelligently loading large hdf5 files from MRED
	If no file name is given, the class looks to the options parser, then finally to whichever *.hdf5 
 	file happens to be loaded first in the working directory (also selectable via command line flag)
	'''
	def __init__(self, filename=None):

		self.filename = filename if filename else options.files 
		self.filename = self.filename if self.filename else [x for x in os.listdir(options.directory) if '.hdf5' in x][0]
		self.histogramTable = {}
		self.saveToTable = options.keep
		self.__nameMap = {}
		self.attrs = {}

		with hp.File(self.filename,'r' ) as f:
			tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
			self.__stringData = [x[0] for x in tables['string_data'][()]]
			self.__strings = tables['strings'][()]
			self.__histograms = tables['histograms'][()]
			for key in f.attrs.keys():
				self.attrs[key] = f.attrs[key]#[0]
			self.__constructNameMap()
			self.histogramNames = list(self.__nameMap.keys())


	def __getHistogramName(self, strings):
		'''
		Converts the ascii stringData array to histogram names	
		@strings is a tuple as given by the strings attribute of the hdf5 table. 
		E.g. tables['strings'] --> [(0, 1), (1, 5), (6, 3), ...] where the first index points to the 
		start of the string in stringData, and the second is the legnth 
		'''
		startIndex = strings[0]
		stringLength = strings[1] - 1
		histogramName = ''.join([chr(self.__stringData[startIndex+x]) for x in range(stringLength)])
		return histogramName

	def getNormFactor(self, nIonsAttr='nIons', gfuAttr='gfu'):
		'''
		Returns the normalization factor by looking for the HDF5 file attributes
		"nIons" and "gfu" (by default). Normalization factor is given by 1 / (gfu * nIons). 
		'''
		try:
			if not options.raw:
				return 1./(self.attrs[nIonsAttr][0] * self.attrs[gfuAttr][0])
		except Exception as e:
			print("Error in getNormFactor()")
			print(e)
			try:
				return 1./(self.attrs[nIonsAttr][0])
			except:
				print("couldn't normalize by ions")
		return 1

	def printAttributes(self):#TODO: REDO this function with the dict as defined above
		pass

	def __constructNameMap(self):
		try:
			for i in self.__histograms:
				histogramName = self.__getHistogramName(self.__strings[i[0]])
				self.__nameMap[histogramName] = (i[1], i[1]+i[2])
		except Exception as e:
			print("Error in Hdf5Data.__constructNameMap() ")
			print(e)

	def revInt(self, df):
		'''"Reverse Integrates" the histogram such that, for standard energy deposition histograms, 
		the "y" values are the cross section for generated a given amount of energy or greater. '''
		df[['y', 'y2']] = df[['y', 'y2']][::-1].cumsum()[::-1]
		return df

	def getHistogram(self, histName=None, diff = options.diff):
		'''	returns only one histogram labelled by @histName for a given file. Defaults to the first histogram if no 
		@histName passed. If options.diff is set to True, the data is given with only the fluence normalization applied; 
		if set to False, the reverse integrated cross section is given. '''
		try:
			histName = histName if histName else list(self.__nameMap.keys())[0]
			print("histogram name: ")
			with hp.File(self.filename, 'r') as f:
				tables = [f['runs'][k] for k in f['runs'].keys()][0]['tables']
				df = pd.DataFrame(tables['histogram_data'][()][ self.__nameMap[histName][0] : self.__nameMap[histName][1] ])
			df.name = histName
			df[['y', 'y2']] *= self.getNormFactor()
			if not diff:
				df = self.revInt(df)
			if self.saveToTable:
				self.histogramTable[histName] = df
			return df
		except Exception as e:
			print("Error in getHistogram() method. ")
			print(e)
	 
	def getHistograms(self, histograms=None):
		'''	returns a dictionary of histogram DataFrames with the names as keys for the histogram names passed 
		as a list. Adds to the histogramTable object attribute if options.keep == True
	 	Defaults behavior is to return all histograms within a given hdf5 file. '''
		output={}
		histograms = histograms if histograms else self.histogramNames
		try:
			for histName, histBounds in self.__nameMap.items():
				if histName in histograms:
					df = self.getHistogram(histName)
					output[histName] = df
			return output
		except Exception as e:
			print("Error in getHistograms() method. ")
			print(e)

	def getTotalDose(self, histName=None, includeUnderflowBin=False):
		histogram = self.getHistogram(histName=histName, diff=True)	
		startIndex = 0 if includeUnderflowBin else 1
		return np.sum(list(histogram['x'] * histogram['y'])[startIndex:])
	


#probably need to put the plotting in another Class / file? 


#f = hp.File(fileNames[0], 'r')
#hists = getAllHistograms(f)
#topHist = getHistogram(f, 'topHist')
#bottomHist = getHistogram(f, 'bottomHist')
#f.close()

#def singlePlot():
#	import matplotlib.pyplot as plt
#	histogram1 = topHist
#	histogram2 = bottomHist
#	colors = ['Blue', 'Red']
#	plt.figure()
#
#	plt.xlim([10**-1, 50])
#	plt.ylim([10**-24, 10**-10])
#
#	plt.gca().set_xscale('log')
#	plt.gca().set_yscale('log')
#	plt.plot(histogram1['x'], histogram1['y'], colors[0],linewidth = 2, alpha=0.75 )#,linestyle='dashed')
#	plt.plot(histogram2['x'], histogram2['y'], colors[1],linewidth = 2, alpha=0.75 )#,linestyle='dashed')
#
#	plt.title('test title')
#	plt.xlabel('Energy Deposited [MeV]')
#	plt.ylabel('Integrated Cross Section [cm^2]')
#	plt.show()
#
#
#class Hdf5Files:
#	def __init__(self, files=[]):
#		'''
#		Sets files attribute to the list explicitly passed, or the list passed via the
#		options parser, or finally all HDF5 files in the directory, in that order
#		'''
#		if files:
#			self.files = files
#		elif options.files:
#			self.files = options.files
#		else:
#			self.files = [x for x in os.listdir('.') if '.hdf5' in x]
#
#	def setAllFiles(self, directory='.'):
#		'''Includes all HDF5 files for a given @directory (defaults to the current dir)'''
#		self.files = [x for x in os.listdir(directory) if '.hdf5' in x]
#
#	def filterFiles(self, filterStrings = [], exact = False):
#		'''Filters out filenames from the files attribute if '''
#		if exact:
#			try:
#				[self.files.remove(x) for x in filterStrings]
#			except ValueError:
#				pass
#		else:
#			for f in filterStrings:
#				self.files = [x for x in self.files if f not in x]		
#	
#	def addFiles(self, filesToAdd=[]):
#		[self.files.append(f) for f in filesToAdd if (os.path.isfile(f) and f not in self.files)]
#
#
#files = Hdf5Files()
#files = files.files
