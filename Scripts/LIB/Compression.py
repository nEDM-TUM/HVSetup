import gzip
from array import array


def gzip_file(filename):
	f = open(filename, 'rb')
	g = gzip.open(filename+'.gz', 'wb')
	g.writelines(f)
	g.close()
	f.close()
	return


def read_gzip_file(filename, separator = '\t', readmode = "rb", comment_char = '#'):
	"""
	Reads a gzipped file. We assume that it consists of rows and columns of floating point data.
	The standard separator assumed for the columns is the tab-character (\t).
	Returns (int)lines_start, (float*)lines, (float*)columns
	:param filename:
	:param separator:
	:return:
	"""
	handle = gzip.open(filename, readmode)
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
	columns = [array('d') for i in range(ncols)]
	for nl in range(lines_start, len(lines)):
		tmp_str = str(lines[nl]).strip().split(separator)
		for nc in range(ncols):
			columns[nc].append(float(tmp_str[nc]))

	return header, lines, columns


def read_gzip_file_with_units(filename, separator = '\t', unitseparator=',', readmode = "rb", comment_char = '#'):
	"""
	Reads a gzipped file. We assume that it consists of rows and columns of floating point data.
	The standard separator assumed for the columns is the tab-character (\t).
	Returns (int)lines_start, (float*)lines, (float*)columns
	:param filename:
	:param separator:
	:return:
	"""
	handle = gzip.open(filename, readmode)
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
	columns = [[array('d'), []] for i in range(ncols)]
	for nl in range(lines_start, len(lines)):
		tmp_str = str(lines[nl]).strip().split(separator)
		for nc in range(ncols):
			tmp_item = tmp_str[nc].split(unitseparator)
			columns[nc][0].append(float(tmp_item[0].strip()))
			columns[nc][1].append(tmp_item[1].strip())

	return header, lines, columns
