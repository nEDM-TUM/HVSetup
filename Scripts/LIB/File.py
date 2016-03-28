import numpy
import os
import re
import sys


def walklevel(some_dir, level=1):
	"""
	Use os.walk() with a specified level of depth
	:param some_dir:
	:param level:
	:return: os.walk() until level of depth is reached
	"""
	some_dir = some_dir.rstrip(os.path.sep)
	assert os.path.isdir(some_dir)
	num_sep = some_dir.count(os.path.sep)
	for root, dirs, files in os.walk(some_dir):
		yield root, dirs, files
		num_sep_this = root.count(os.path.sep)
		if num_sep + level <= num_sep_this:
			del dirs[:]


def set_directory(directory, ask=True):
	while not os.path.exists(directory):
		print "'" + directory + "' does not exist!"
		if ask:
			cin = raw_input("Provide a new one (or '+' to create it, or '#' to quit): ")
		else:
			cin = "+"
		if cin == "+":
			os.makedirs(directory)
		elif cin == "#":
			sys.exit(0)
		else:
			directory = cin
	return directory


def get_subdirectories(dir, join = False):
	"""

	:param dir: base directory
	:param join: join the paths of sub-directories and dir to provide an absolute path
	:return: list of strings with all subdirectories in dir
	"""
	subdirs = []
	for dirname, dirnames, filenames in walklevel(dir, 0):
		for subdirname in dirnames:
			if join:
				subdirs.append([dirname, subdirname])
			else:
				subdirs.append(subdirname)
	return subdirs


def get_filenames(dir, join=False):
	"""

	:param dir:
	:param join:
	:return:
	"""
	files = []
	for dirname, dirnames, filenames in walklevel(dir, 0):
		for filename in filenames:
			if join:
				files.append([dirname, filename])
			else:
				files.append(filename)
	return files


def select_folders(base_directory):
	"""
	Get all directories and print them.
	Selection will work as of now either with 0 (all) or by a single number.
	:return:
	"""
	directory_list = get_subdirectories(base_directory, True)
	if len(directory_list) == 0:
		print "No sub-directories found! Aborting..."
		sys.exit(1)
	print "\n" + "Showing list of subdirectories:"
	for i in range(len(directory_list)):
		print "[" + str(i + 1) + "]\t" + directory_list[i][1]
	cin = -1
	while cin > len(directory_list) or cin < 0:
		cin = raw_input("Select folder by number, q for quit, 0 for all [1]: ")
		if cin == 'q':
			sys.exit(0)
		try:
			cin = int(cin)
		except ValueError:
			cin = -1
	# create directory list, best case: list with one element
	if cin == 0:
		selected_folders = [directory[0] + "/" + directory[1] for directory in directory_list]
		#directory_list
		return True, selected_folders
	else:
		#selected_folders = [directory_list[cin - 1]]
		selected_folders = [directory_list[cin - 1][0] + "/" + directory_list[cin - 1][1]]
		return False, selected_folders


def select_files(directory_list, all_folders = False):
	"""
	Get all files from the selected sub-directories.
	If code '0', so all dirs were chosen, we just take all files from these dirs!
	Again, the selection will work with either 0 (all) or a number corresponding to the printed list.
	However, here you may input a list of files in a comma-separated fashion.
	:param directory_list:
	:param all_folders:
	:return:
	"""
	selected_filenames = []
	selected_all = False
	# list all files in dir, if all_folders were chosen, list all files
	if len(directory_list) == 0:
		print "Directory list is empty! Aborting..."
		sys.exit(2)
	if all_folders:
		print "\n" + "Using all files from all subdirs..."
		for directory in directory_list:
			selected_filenames += get_filenames(directory[0] + directory[1])
		selected_all = True
	else:
		print "\n" + "Showing list of filenames:"
		filename_list = get_filenames(directory_list[0], True)
		for i in range(len(filename_list)):
			print "[" + str(i + 1) + "]\t" + filename_list[i][1]
		cin = -1
		while cin > len(filename_list) or cin < 0:
			cin = raw_input("Select the files for analysis, q for quit, 0 for all, separate with comma [0]: ")
			if cin == "":
				cin = "0"
			elif cin == "q":
				sys.exit(0)
			tmp_list = cin.split(",")
			if len(tmp_list) == 1:
				try:
					cin = int(tmp_list[0])
				except ValueError:
					cin = -1
				if cin >= 0 and cin <= len(filename_list):
					if cin == 0:
						selected_filenames = [filename[0] + "/" + filename[1] for filename in filename_list]
						selected_all = True
					else:
						selected_filenames.append(filename_list[cin - 1][0] + "/" + filename_list[cin - 1][1])
			else:
				for item in tmp_list:
					try:
						item = int(item)
					except ValueError:
						cin = -1
						continue
					if int(item) > len(filename_list) or int(item) < 1:
						continue
					else:
						selected_filenames.append(filename_list[int(item) - 1][0] + "/" + filename_list[int(item) - 1][1])
					cin = item
	return selected_all, selected_filenames


def get_filename_filecount(dir, pattern_begin):
	"""
	CREATE A NEW FILE WITH INCREASING FILE COUNT
	"""
	i = 1
	while True:
		files = [True for f in os.listdir(dir) if re.match(r'' + pattern_begin+("%0*d" % (4, i)) + '.*', f)]
		if len(files) == 0:
			break
		i += 1
	filename = pattern_begin + ("%0*d" % (4, i)) + '.dat'
	return filename


def read_file(filename, separator='\t', inter_separator=',', channel_separator=':', readmode="r", comment_char='#'):
	"""
	Reads a normal file. We assume that it consists of rows and columns of floating point data,
	which may consist of x and y data in the format dataX1,dataY1\tdataX2,dataY2.
	The standard separator assumed for the columns is the tab-character (\t).
	Returns (char**)header, (float*)lines, (float**)columns
	:param filename:
	:param separator:
	:return:
	"""
	handle = open(filename, readmode)
	lines = handle.readlines()
	handle.close()
	lines_start = 0
	header = []
	for i in range(len(lines)):
		if str(lines[i]).lstrip()[0] == comment_char:
			tmp = str(lines[i]).replace(comment_char, '').split(':')
			if len(tmp) == 1:
				header.append([tmp[0].strip()])
			else:
				header.append([tmp[0].strip(), tmp[1].strip()])
			continue
		lines_start = i
		break

	ncols = len(str(lines[lines_start]).split(separator))
	columns = [[] for i in range(ncols)]

	"""
	for s in str(lines[lines_start]).split(separator):
		nchannels = len(s.split(channel_separator)) if len(s.split(channel_separator)) > nchannels else nchannels
		for s2 in s.split(channel_separator):
			ninter = len(s2.split(inter_separator)) if len(s2.split(inter_separator)) > ninter else ninter
	"""

	for nl in range(lines_start, len(lines)):
		tmp_columns = str(lines[nl]).strip().split(separator)
		for nc in range(ncols):
			columns[nc].append(tmp_columns[nc])
			"""
			tmp_channels = tmp_columns[nc].split(channel_separator)
			for nch in range(len(tmp_channels)):
				tmp_item = tmp_channels[nch].split(inter_separator)

				if len(columns[nc]) < len(tmp_item):
					columns[nc] = [numpy.array([]) for i in range(len(tmp_item))]
				for inter_id in range(len(tmp_item)):
					columns[nc][inter_id] = numpy.append(columns[nc][inter_id], float(tmp_item[inter_id].strip()))
			"""

	return header, lines, columns
