#!/usr/bin/python
__all__ = ['files']
import os
from ._options_parser import options

class Hdf5Files:
	def __init__(self, files=[]):
		'''Sets the current files attribute to the list explicitly passed, or the list passed via the
		options parser, or finally all HDF5 files in the directory, in that order		'''
		if files:
			self.current = files
		elif options.files:
			self.current = options.files
		else:
			self.current = [options.directory + x for x in os.listdir(options.directory) if '.hdf5' in x]
			self.filenames =  [x for x in os.listdir(options.directory) if '.hdf5' in x]

	def dropFiles(self, dropFilters, exact = False):
		'''Updates the current file list, droppinng files which match the filterString(s).'''
		if type(dropFilters) == str:
			self.dropFiles([dropFilters], exact = exact)
		else:
			if exact:
				[self.current.remove(x) for x in dropFilters if x in self.current]
			else:
				[self.current.remove(x) for x in self.current for fs in dropFilters if fs in x]
	
	def selectFiles(self, selectFilters, exact = False):
		'''Updates the current file list to only include those file(s) which match the filterString(s)'''
		if type(selectFilters) == str:
			self.selectFiles([selectFilters], exact = exact)
		else:
			if exact:
				self.current = [x for x in selectFilters if x in self.current]
			else:
				self.current = [x for x in self.current for fs in selectFilters if fs in x]

	def addFiles(self, filesToAdd):
		[self.current.append(f) for f in filesToAdd if (os.path.isfile(f) and f not in self.current)]

	def resetFiles(self, select=None, directory='.', exact = False):
		'''Resets the current file list, with the option to filter and select only files that partially match 
			the @select (@exact=False, default) or that exactly match @select (@exact=True)'''
		self.current = [x for x in os.listdir(directory) if '.hdf5' in x]
		if select: 
			self.selectFiles(select, exact) 
	
	def listFiles(self, attribute=''):
		'''Lists the current files in one column for easier reading. If a file attribute (set at run time in MRED) 
		is passed, the value of that attribute for each file is also presented. set @attribute = 'all' to return all 
		HDF5 file attributes associated with each file.'''
		from ._data import Hdf5Data
		if attribute:
			for f in self.current:
				fileName = f.split("/")[-1]
				print(f"{fileName}")
				attrs = list(Hdf5Data(f).attrs.items())
				for a in attrs:
					if attribute in a[0] or attribute=='all':
						try:
							print("\t{:<15}\t{:<15}".format(str(a[0]), str(a[1])))
						except:
							print("ERROR: with printing the attribute(s) for {f}".format(f))
				print("----------------------------------------------")
		else:
			print('\n'.join(self.current))


files = Hdf5Files()
