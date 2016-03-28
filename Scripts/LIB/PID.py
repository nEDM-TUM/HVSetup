import numpy

class PID(object):

	def __init__(self, P=0., I=0., D=0., Imin=-500, Imax=500, nsize=100):
		self.P, self.I, self.D = P, I, D
		self.Imin, self.Imax = Imin, Imax
		self.TermP, self.TermI, self.TermD = 0.0, 0.0, 0.0
		self.setpoint, self.measure, self.moutput, self.output = 0., 0., 0., 0.
		self.error = 0.0
		self.manual = False
		self.UseP, self.UseI, self.UseD = True, False, False
		self.data = numpy.zeros(nsize)
		self.INTEGRAL, self.DIFFERENCE = 0, 0

	def SetStateOutput(self, state="PID"): self.manual = True if state=='MAN' else False
	def SetManualOutput(self, moutput = None):
		self.SetStateOutput("MAN")
		self.moutput = moutput if not moutput is None else 0.0
	
	def GetP(self): return self.P
	def GetI(self):	return self.I
	def GetD(self):	return self.D
	def SetP(self, P): self.P = P
	def SetI(self, I): self.I = I
	def SetD(self, D): self.D = D
	def SetStateP(self, state=True): self.UseP = state
	def SetStateI(self, state=True): self.UseI = state
	def SetStateD(self, state=True): self.UseD = state
	def SetSetpoint(self, setpoint): self.setpoint = setpoint
	def ClearData(self): self.data = numpy.zeros(len(self.data))

	def update(self):
		if not self.UseP:
			self.output = 0.0
			return 0.0
		self.TermP = self.P * self.error
		self.TermI = (self.P * self.I * self.INTEGRAL) if self.UseI else 0.
		self.TermD = -(self.P * self.D * self.DIFFERENCE) if self.UseD else 0.
		if not self.manual:
			self.output = self.TermP + self.TermI + self.TermD
		else:
			self.output = self.moutput
		return self.output

	def feed(self, value):
		self.measure = value
		self.error = self.setpoint - value
		self.data[0] = self.error
		self.data = numpy.roll(self.data, -1)
		if 0 <= numpy.fabs(numpy.trapz(self.data) * self.P) < 100.0:
			self.INTEGRAL = numpy.trapz(self.data)
		np_diff = numpy.diff(self.data)
		nonzero = numpy.nonzero(np_diff)[0]
		if len(nonzero) > 0 and nonzero[-1] > 0:
			self.DIFFERENCE = np_diff[nonzero[-1]] / (len(np_diff)-nonzero[-1]-1.)
		else:
			self.DIFFERENCE = np_diff[-1]
		self.update()

