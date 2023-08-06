from __future__ import division, absolute_import, print_function
import ctypes as _ctypes
import os as _os
from ._request import request

_so_file = _os.path.dirname(__file__) + '/lib/libcoral-api_python.so'
_c_api = _ctypes.CDLL(_so_file)
# environment values
__CORAL_IP__ = _ctypes.c_int.in_dll(_c_api, "CORAL_IP").value
__CORAL_PORT__ = _ctypes.c_int.in_dll(_c_api, "CORAL_PORT").value
# wire functions
_c_api.wire_open.argtypes = [_ctypes.c_uint, _ctypes.c_int]
_c_api.wire_open.restype = _ctypes.c_void_p
_c_api.wire_close.argtypes = [_ctypes.c_void_p]
_c_api.wire_close.restype = _ctypes.c_int
_c_api.wire_write_UTF.argtypes = [_ctypes.c_void_p, _ctypes.c_char_p]
_c_api.wire_write_UTF.restype = _ctypes.c_int
_c_api.wire_write_bytes.argtypes = [_ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_int]
_c_api.wire_write_bytes.restype = _ctypes.c_int
_c_api.wire_sync.argtypes = [_ctypes.c_void_p]
_c_api.wire_sync.restype = _ctypes.c_int


# This class contains a wire, and exists to be able to check if the arguement of
# the wait function is the correct type

class session:
	__name__ = 'session'
	__module__ = 'inaccel.coral'
	def __init__(self, w):
		self.__wire__ = w

def submit(req):
	if not isinstance(req, request):
		raise TypeError('Only inaccel coral requests can be submitted to coral')
	w = _c_api.wire_open(__CORAL_IP__, __CORAL_PORT__);
	if not w:
		raise RuntimeError('Connection Failed: Connection refused')
	# get the packet from the request
	packet = req.pack()
	# send the packet
	bytes_sent = _c_api.wire_write_UTF(w, _ctypes.c_char_p(packet[0].encode('utf-8')))
	if(bytes_sent < 0):
		raise RuntimeError('Connection Failed: Failed to send the request')
	bytes_sent = _c_api.wire_write_bytes(w, _ctypes.c_char_p(packet[1]), packet[2])
	if(bytes_sent < 0):
		raise RuntimeError('Connection Failed: Failed to send the request')
	# return a session
	return session(w)

def wait(sess):
	if not isinstance(sess, session):
		raise TypeError('Only inaccel coral sessions can be waited')
	# wait session
	ret = _c_api.wire_sync(sess.__wire__)
	if(ret < 0):
		raise RuntimeError('Connection Failed: Request could not be handled.')
	_c_api.wire_close(sess.__wire__)
