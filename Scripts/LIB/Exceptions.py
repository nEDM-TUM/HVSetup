__author__ = 'Christian Velten'

import socket
#import usb.core # problem on WIN w/ pyusb

class SocketException(socket.error):
	pass


class SocketConnectionException(SocketException):
	pass


class SocketTalkError(SocketException):
	pass


#class USBException(usb.core.USBError):
class USBException(object):
	pass


class USBIOException(USBException):
	pass

