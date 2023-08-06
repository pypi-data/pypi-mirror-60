import pandas as pd
from .datatools import options, _HistogramList

class TxtData(_HistogramList):
	def __init__(self):
		self.__filenames = [x + " - data" for x in options.files if ".txt" in x]
		super().__init__(self.__filenames)	

		for filename in options.files:
			df = pd.read_csv("TestSave.txt", delimiter="\t", header = None)
			df = df.loc[: len(df)/2]
			df.columns = ['x', 'y', 'y2', 'xy', 'x2y', 'n', 'w']
			self.histogramsDict[filename + " - data"].df = df

		self.__getNormalizationInfo()
		options.fullpath=True

	def __getNormalizationInfo(self):
		print("Getting information for normalization (pickle files loaded" )
		for filename in self.__filenames:
			self.normalize(filename)

	def normalize(self, filename):
		print("-----------------------------")
		print("filename: {}".format(filename))
		while True:
			try:
				nIons = int(input("\tnIons: "))
				gfu = float(input("\tgun fluence unit: "))
				break
			except KeyboardInterrupt:
				return False
			except:
				print("ERROR: enter a valid value")
		for name, histogram in self.histogramsDict.items():
			if filename in name:
				histogram.normFactor = gfu * nIons
				histogram.normalize()
