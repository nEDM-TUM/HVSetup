import math

ms = 1E-3
us = 1E-6
ns = 1E-9


def get_largest_array_length(array_list):
	"""

	:param array_list: list of arrays
	:return: largest length of all arrays provided in array_list
	"""
	list_len = len(array_list)
	largest = 0
	for i in range(list_len):
		if len(array_list[i]) > largest:
			largest = len(array_list[i])
	return largest


def is_power(val, base=2):
	if base == 1 and val != 1: return False
	if base == 1 and val == 1: return True
	if base == 0 and val != 1: return False
	power = int(math.log(val, base) + 0.5)
	return base ** power == val


def dictinvert(d):
    inv = {}
    for k, v in d.iteritems():
	keys = inv.setdefault(v, [])
	keys.append(k)
    return inv
