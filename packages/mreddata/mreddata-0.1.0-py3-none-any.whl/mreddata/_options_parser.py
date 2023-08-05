__all__ = ['options', 'resetOptions']
import argparse, sys
def resetOptions():                                                                                                                                       
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', '-d', type=str, default='.', help='Directory path for the HDF5 files. All files should be in the same directory (defaults to the current working directory)')  #TODO: add features for combining files from several folders
    parser.add_argument('-a', '--all', action='store_true', default=False, help='Automatically gather all of the histograms from all HDF5 **files** in the working directory. Returns dictionary object sorted by filename and then histogram name')
    parser.add_argument('-f', '--files' , type=str, nargs="+", default=[], help='Only load data from the HDF5 files listed after this flag (rather than every HDF5 in the directory)')
    parser.add_argument('--raw', action='store_true', default=False, help='only return the raw data, with no normalization / post processing applied (default is normalized the gun fluence unit and nIons)')
    parser.add_argument('--diff', action='store_true', default=False, help='differntial data (default is reverse-integrated)')
    parser.add_argument('-k', '--keep', action='store_true', default=False, help='keep histograms, once generated, in a dictionary attribute of the Hdf5Data object for easier/faster access. Not a good idea to use this on files with many histograms')
    options, __remaining = parser.parse_known_args(sys.argv[1:])
    return options

options = resetOptions()
options.directory = options.directory +'/' if options.directory[-1] != '/' else options.directory
