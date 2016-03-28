"""
s.advantest_locked                 s.device                           s.last_btag                        s.pack_vendor_specific_out_header  s.timeout
s.advantest_quirk                  s.get_capabilities                 s.local                            s.pulse                            s.trigger
s.advantest_read_myid              s.iSerial                          s.lock                             s.read                             s.unlock
s.ask                              s.idProduct                        s.max_recv_size                    s.read_raw                         s.unpack_bulk_in_header
s.ask_raw                          s.idVendor                         s.pack_bulk_out_header             s.read_stb                         s.unpack_dev_dep_resp_header
s.bulk_in_ep                       s.iface                            s.pack_dev_dep_msg_in_header       s.remote                           s.write
s.bulk_out_ep                      s.interrupt_in_ep                  s.pack_dev_dep_msg_out_header      s.reset                            s.write_raw
s.clear                            s.is_usb488                        s.pack_vendor_specific_in_header   s.term_char                        
"""
from LIB.STD import is_power

#
# ----------------------------------------------------------------------------------------------------------------------------
#
queriesMeasuInfo = ["TYPE", "SOURCE", "COUNT"]
queriesMeasuMinimal = ["VALUE"]
queriesMeasuMinimalStat = ["VALUE", "MEAN", "STDDEV"]
queriesMeasuNormal = ["VALUE", "MEAN", "MINIMUM", "MAXIMUM", "STDDEV"]
queriesMeasuFull = ["TYPE", "SOURCE", "COUNT", "VALUE", "MEAN", "MINIMUM", "MAXIMUM", "STDDEV", "UNITS"]

queriesChannelInfo = ["BANDWIDTH", "INVERT", "LABEL", "OFFSET", "POSITION", "SCALE", "TERMINATION", "YUNITS"]

#
# ----------------------------------------------------------------------------------------------------------------------------
#


def dict2string(d, parseFull=True, filterset=None):
	tmp = ""
	for key in d.keys():
		if not filterset is None:
			if not key in filterset: continue
		if parseFull:
			tmp += key+':'+d[key]+'\t'
		else:
			tmp += d[key]+'\t'
	return tmp


def get_values(s, objstr, queries):
	values = []
	s.cmd("*WAI")
	for query in queries:
		values.append( (query, s.cmd_and_return(objstr+query+'?').strip().replace('"', '')) )
	return dict(values)


def set_values(s, objstr, queries, values):
	n = len(queries) if len(queries) <= len(values) else len(values)
	for i in range(n):
		s.cmd(objstr+queries[i]+' '+values[i])
	s.cmd("*WAI")
	return


def get_values_channel(s, ch, queries=queriesChannelInfo):
	if ch < 1 or ch > 4:
		raise ValueError("Channel index out of range (1-4)!")
	chstr = "CH" + str(ch) + ':'
	return get_values(s, chstr, queries)


def get_values_measurement(s, measu_n, queries=queriesMeasuNormal):
	mstr = "MEASUREMENT:MEAS" + str(measu_n) + ':'
	return get_values(s, mstr, queries)


def setup_measurement_mean(s, channels=[1,2,3,4], statistics=True, statistics_samples=20):
	print "Setting up measurements:"
	#s.cmd("MEASU:GATing SCREen")
	if statistics:
		s.cmd("MEASU:STATIstics:MODe ON")
		s.cmd("MEASU:STATIstics:WEIghting "+str(statistics_samples))
		s.cmd("MEASU:STATIstics RESET")
		print "\tenabled statistics, weighting: "+str(statistics_samples)+" samples"
	elif statistics_samples != -1:
		s.cmd("MEASU:STATISTICS:MODE OFF")
	for i in range(len(channels)):
		print "\tmeasurement: MEAN (CH{0})".format(channels[i])
		s.cmd("MEASUREMENT:MEAS{0}:SOURCE CH{1}".format(i+1, channels[i]))
		s.cmd("MEASUREMENT:MEAS{0}:TYPE MEAN".format(i+1))
		s.cmd("MEASUREMENT:MEAS{0}:STATE ON".format(i+1))
	s.cmd("*WAI")
	return


def setup_acquire(s, mode='SAMPLE', num=2):
	valid_modes = ['SAMPLE', 'AVERAGE']
	print "Setting up ACQUIRE:"
	if not mode in valid_modes:
		raise ValueError('Invalid oscilloscope acquire mode (\'{0}\') provided!'.format(mode))
	s.cmd('ACQUIRE:MODE {0}'.format(mode))
	print "\t  MODE: {0}".format(mode)
	if mode == 'AVERAGE':
		s.cmd('ACQUIRE:NUMAVG {0}'.format(num if is_power(num, 2) else 2))
		s.cmd('ACQUIRE:STOPAFTER RUNSTOP')
		s.cmd('ACQUIRE:STATE RUN')
		print "\tNUMAVG: {0} (STOPAFTER: RUNSTOP, STATE: RUN)".format(num if is_power(num, 2) else 2)
	s.cmd("*WAI")
	return
#
# ----------------------------------------------------------------------------------------------------------------------------
#
