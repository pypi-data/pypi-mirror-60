from __future__ import division, absolute_import, print_function
import ctypes as _ctypes
import os as _os
import numpy as _np
from ._numpy_array import ndarray
import binascii as _binascii

so_file = _os.path.dirname(__file__) + '/lib/libcoral-api_python.so'
c_api = _ctypes.CDLL(so_file)
# environment values
__INACCEL_NAMESPACE__ = _ctypes.c_char_p.in_dll(c_api, "INACCEL_NAMESPACE").value
__PID__ = _ctypes.c_int.in_dll(c_api, "pid").value
# cube functions
c_api.cube_getid.argtypes = [_ctypes.c_void_p]
c_api.cube_getid.restype = _ctypes.c_char_p

"""Inaccel Coral Request
"""

class request:
	__name__ = 'request'
	__module__ = 'inaccel.coral'

	def __init__(self, type=None):
		if not (isinstance(type, str) or type is None):
			raise TypeError('Request type must be a string')
		self.__type__ = type
		self.__arguments__ = []

	def __arg__(self, index, key, value):
		if index >= len(self.__arguments__):
			self.__arguments__.extend([(None,None) for x in range(len(self.__arguments__), index + 1)])
		self.__arguments__[index] = (key, value)

	def type(self, type):
		if not isinstance(type, str):
			raise TypeError('Request type must be a string')
		self.__type__ = type
		return self

	def pack(self):
		if self.__type__ is None:
			raise TypeError('Wrong request format, request type is empty!')
		_arg_sizes = str()
		_arg_values = bytearray()
		_payload_size = 0
		first = True
		for index in range(len(self.__arguments__)):
			# Read all argument tuples
			(key, value) = self.__arguments__[index]
			# If any of the fields is empty raise exception
			if key is None or value is None:
				raise TypeError('Wrong request format, value of argument index ' + str(index) + ' is empty!')
			if first:
				first = False
			else:
				_arg_sizes += ','
			if key is 'Cube':
				_arg_sizes += key
				_payload_size += 6
			else:
				_arg_sizes += str(key)
				_payload_size += key
			_arg_values.extend(value)

		# Convert the _arg_values bytearray to an immutable bytes type
		_payload = bytes(_arg_values)
		# Create the header
		_header = self.__type__ + '|' + str(_payload_size) + '|' + str(__PID__) + '@'  + __INACCEL_NAMESPACE__.decode("utf-8") + '|' + _arg_sizes
		return (_header, _payload, _payload_size)

	def view_packet(self):
		if self.__type__ is None:
			raise TypeError('Wrong request format, request type is empty!')
		_arg_sizes = str()
		_arg_values = bytearray()
		_payload_size = 0
		first = True
		for index in range(len(self.__arguments__)):
			# Read all argument tuples
			(key, value) = self.__arguments__[index]
			# If any of the fields is empty raise exception
			if key is None or value is None:
				raise TypeError('Wrong request format, value of argument index ' + str(index) + ' is empty!')
			if first:
				first = False
			else:
				_arg_sizes += ','
			if key is 'Cube':
				_arg_sizes += key
				_payload_size += 6
				_arg_values.extend(value)
			else:
				_arg_sizes += str(key)
				_payload_size += key
				_arg_values.extend(_binascii.hexlify(value))

		# Create the header
		_header = self.__type__ + '|' + str(_payload_size) + '|' + str(__PID__) + '@'  + __INACCEL_NAMESPACE__.decode("utf-8") + '|' + _arg_sizes
		print('Header: ' + _header)
		print('Payload: ' + _arg_values.decode())

	def view_string(self):
		if self.__type__ is None:
			raise TypeError('Wrong request format, request type is empty!')
		_arg_sizes = str()
		_arg_values = str()
		_payload_size = 0
		first = True
		for index in range(len(self.__arguments__)):
			# Read all argument tuples
			(key, value) = self.__arguments__[index]
			# If any of the fields is empty raise exception
			if key is None or value is None:
				raise TypeError('Wrong request format, value of argument index ' + str(index) + ' is empty!')
			if first:
				first = False
			else:
				_arg_sizes += ','
			if key is 'Cube':
				_arg_sizes += key
				_payload_size += 6
				_arg_values += '\t ' + key + '\t{' + value.decode("utf-8") + '}\n'
			else:
				_arg_sizes += str(key)
				_payload_size += key
				value_tmp = bytearray(value)
				value_tmp.reverse()
				_arg_values += '\t ' + str(key) + '\t{0x' + _binascii.hexlify(value_tmp).decode() + '}\n'

		# Create the header
		_header = self.__type__ + '|' + str(_payload_size) + '|' + str(__PID__) + '@'  + __INACCEL_NAMESPACE__.decode("utf-8") + '|' + _arg_sizes
		_string = 'Header: ' + _header + '\n' + 'Payload: Size\tValue\n' + _arg_values
		return _string

	def __get_parent_recursive__(self, value):
		if value.base is None:
			pointer, read_only_flag = value.__array_interface__['data']
			cube_id = c_api.cube_getid(pointer)
			if not cube_id:
				raise RuntimeError('Failed to read cube id from metadata')
			return cube_id
		else:
			return get_parent_recursive(value.base)

	def __convert__(self, value):
		if isinstance(value, _np.bool):
			tmp = _np.uint8(value)
			return tmp.nbytes, tmp.newbyteorder('L').tobytes()
		elif isinstance(value, (_np.integer, _np.floating, _np.complexfloating)):
			return value.nbytes, value.newbyteorder('L').tobytes()
		elif isinstance(value, _np.ndarray) or isinstance(value, ndarray):
			raise TypeError('ndarrays inside tuples not supported, please send them as separate arguments')
		else:
			raise TypeError('Value type '+str(type(value))+' not supported, please use numpy primitive types and inaccel coral ndarrays')

	def arg(self, value, index=None):
		if index is None:
			index = len(self.__arguments__)

		# if isinstance(value, INnp.ndarray):
		# 	if value.base is None:
		# 		pointer, read_only_flag = value.__array_interface__['data']
		# 		id = c_api.cube_getid(pointer)
		# 		self.__arg__(index, 'cube', id)
		# 		return self
		# 	elif allow_cube_child:
		# 		id = self.__get_parent_recursive__(value.base)
		# 		self.__arg__(index, 'cube', id)
		# 		return self
		# 	else:
		# 		raise TypeError('Cube argument must be parent Cube, or set allow_cube_child to True')

		if isinstance(value, ndarray):
			if value.iscube():
				self.__arg__(index, 'Cube', value.id)
			else:
				raise TypeError('Cube argument cannot be slice or view of inaccel coral ndarray')
		elif isinstance(value, tuple):
			value_bytes = bytearray()
			value_size = 0
			for var in value:
				converted = self.__convert__(var)
				value_size += converted[0]
				value_bytes.extend(converted[1])
			self.__arg__(index, value_size, value_bytes)
		elif isinstance(value, _np.ndarray):
			self.__arg__(index, value.nbytes, value.tobytes())
		else:
			converted = self.__convert__(value)
			self.__arg__(index, converted[0], converted[1])
		return self

	# def __add__(self, value):
	# 	self.arg(value)
	# 	return self

	def __repr__(self):
		return self.__module__+'.'+self.__name__
