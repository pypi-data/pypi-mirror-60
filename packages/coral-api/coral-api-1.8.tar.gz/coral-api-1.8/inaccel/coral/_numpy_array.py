from __future__ import division, absolute_import, print_function
import ctypes as _ctypes
import os as _os
import numpy as _np

_so_file = _os.path.dirname(__file__) + '/lib/libcoral-api_python.so'
_c_api = _ctypes.CDLL(_so_file)
# cube functions
_c_api.cube_alloc.argtypes = [_ctypes.c_ulong]
_c_api.cube_alloc.restype = _ctypes.c_void_p
_c_api.cube_free.argtypes = [_ctypes.c_void_p]
_c_api.cube_free.restype = _ctypes.c_int
_c_api.cube_getid.argtypes = [_ctypes.c_void_p]
_c_api.cube_getid.restype = _ctypes.c_char_p

"""This array allocates shared memory using mmapped files. It is
 intended for use with InAccel Coral framework. Any requests sent to InAccel
 Coral must have the pointers populated with Inaccel ndarrays
"""
class ndarray(_np.ndarray):
	__name__ = 'ndarray'
	__module__ = 'inaccel.coral'
	__array_priority__ = 100.0

	def __new__(subtype, shape, dtype=_np.float64, order=None):
		# Calculate size in bytes using shape and dtype
		_dbytes = _np.dtype(dtype).itemsize
		if not isinstance(shape, tuple):
			size = _np.uint64(shape)
		else:
			size = _np.uint64(1)
			for k in shape:
				size *= k
		bytes = _np.uint64(size*_dbytes)
		# Create cube using InAccel C api
		mm = _c_api.cube_alloc(bytes)
		if mm is None:
			raise RuntimeError('Cube Allocation failed.')
		# Get cube id using InAccel C api
		cube_id = _c_api.cube_getid(mm)
		if not cube_id:
			raise RuntimeError('Failed to read cube id from metadata')
		# Create a buffer from the pointer
		cube_buffer = (_ctypes.c_byte*bytes).from_address(mm)
		# Create ndarray of our SubClass that uses the cube buffer
		self = super(ndarray, subtype).__new__(subtype, shape, dtype, cube_buffer, order=order)
		# Keep the buffer and cube id
		self.cube = cube_buffer
		self.id = cube_id
		return self

	def __array_finalize__(self, obj):
		# If called by the constructor, obj is None, nothing to do
		if obj is None: return
		elif isinstance(obj, ndarray):
			if hasattr(obj, 'cube') and hasattr(obj, 'id') and self.base is obj:
			# If called by creating a slice, copy pointer and id
				self.cube = obj.cube
				self.id = obj.id
			else:
			# If called by copy, self is ndarray
				self.cube = None
				self.id = None
			# 	raise TypeError('obj is not parent cube?')
		else:
			# If called by a view, throw exception
			raise TypeError('View as Cube not Supported, '
							'please construct new Cube with inaccel.array()')

	def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
		# First get all inputs
		args = []
		for i, input_ in enumerate(inputs):
			# if any inputs are Cubes, view them as ndarrays
			if isinstance(input_, ndarray):
				args.append(input_.view(_np.ndarray))
			else:
				args.append(input_)
		# Then get all outputs
		outputs = kwargs.pop('out', None)
		if outputs:
			out_args = []
			for j, output in enumerate(outputs):
			# if any outputs are Cubes, view them as ndarrays
				if isinstance(output, ndarray):
					out_args.append(output.view(_np.ndarray))
				else:
					out_args.append(output)
			kwargs['out'] = tuple(out_args)
		else:
			outputs = (None,) * ufunc.nout

		# Call the Universal Function from ndarray
		results = super(ndarray, self).__array_ufunc__(ufunc, method, *args, **kwargs)
		if results is NotImplemented:
			return NotImplemented

		if ufunc.nout == 1:
			results = (results,)

		# For all results and outputs as tuples,
		# if the output is not None return it,
		# if the output is None create a Cube from the
		# result ndarray and return that
		results = tuple(((array(result) if isinstance(result, _np.ndarray) else result)
						 if output is None else output)
						for result, output in zip(results, outputs))

		return results[0] if len(results) == 1 else results

	# def __array_function__(self, func, types, inputs, kwargs):
	# 	print(f'inside __array_function__ {func} ')
	# 	print(types)
	# 	args = []

	# 	for input_ in inputs:
	# 		# if any inputs are Cubes, view them as ndarrays
	# 		if isinstance(input_, ndarray):
	# 			# print('type' + type(input_.view(_np.ndarray)))
	# 			args.append(input_.view(_np.ndarray))
	# 		else:
	# 			args.append(input_)

	# 	print(args)
	# 	# if another input has __array_function__ defined, their version will be
	# 	# called with the inaccel ndarray inputs viewed as numpy ndarray inputs
	# 	# so it should work without problems
	# 	results = super(ndarray, self).__array_function__(func, types, args, kwargs)
	# 	# results = func(*args, **kwargs)

	# 	# res = super(ndarray, self).__array_function__(func, types, args, kwargs)
	# 	# if isinstance(res, _np.ndarray):
	# 	# 	print('__array_function__ new cube')
	# 	# 	return ndarray(input_array=res)
	# 	# else:
	# 	# 	return res

	def __array_wrap__(self, res, context=None):
		if isinstance(res, _np.ndarray):
			return ndarray(input_array=res)
		else:
			return res

	def __getitem__(self, indx):
		# Call _np.ndarray __getitem__ from our subclass
		obj = super(ndarray, self).__getitem__(indx)
		# Check if result is ndarray Class but without cube
		if isinstance(obj, ndarray) and obj.cube is None:
			# View as _np.ndarray, since that's what it is
			return obj.view(type=_np.ndarray)
		return obj

	def __del__(self):
		if hasattr(self, 'cube') and not self.cube is None and isinstance(self.base, type(self.cube)):
			ret = _c_api.cube_free(_ctypes.byref(self.cube))
			if(ret < 0):
				raise RuntimeError('Cube Deallocation failed.')


	def copy(self):
		return ndarray(input_array=self)

	def astype(self, dtype, order='K', casting='unsafe'):
		return ndarray(input_array=super(ndarray, self).astype(dtype, order, casting, False, True))

	# def choose(self, choices, out=None, mode='raise'):
	# 	print("asd")
	# 	res = super(ndarray, self).choose(choices, out, mode)
	# 	if out is None:
	# 		return ndarray(input_array=res)
	# 	else:
	# 		return res



	def iscube(self):
		return (hasattr(self, 'cube') and not self.cube is None and isinstance(self.base, type(self.cube)))

	def ischild(self,obj):
		if(isinstance(obj, ndarray) and hasattr(obj, 'cube') and hasattr(obj, 'id')):
			return (isinstance(self, ndarray) and hasattr(self, 'cube') and hasattr(self, 'id') and (self.base is obj))
	# def __repr__(self):
	# 	return '%s(%r)' % (type(self).__name__, self.value)


def array(object, dtype=None, order='K', ndmin=0):
	"""Construct an inaccel ndarray from a wide-variety of objects.
	"""
	# Convert the input object to array_like
	arr = _np.asarray(object).view(_np.ndarray)
	# Overwrite the shape and dtype with the input_array fields
	shape = arr.shape
	# Compute dtype, if input None keep object dtype
	if dtype is not None:
		dtype = _np.dtype(dtype)
	else:
		dtype = arr.dtype

	# Compute order, same as numpy array creation
	if order is 'K':
		if arr.flags.c_contiguous:
			order = 'C'
		elif arr.flags.f_contiguous:
			order = 'F'
		else:
			order = None
	elif order is 'A':
		if arr.flags.f_contiguous and not arr.flags.c_contiguous:
			order = 'F'
		else:
			order = 'C'

	# Compute shape, if ndmin larger than current dimentions, extend shape filled with ones
	if isinstance(shape, tuple):
		nd = len(shape)
	else:
		nd = 1
	if nd < ndmin:
		extention = (1,)*(ndmin-nd)
		extention_access = (0,)*(ndmin-nd)
		if not isinstance(shape, tuple):
			shape = extention + (shape,)
		else:
			shape = extention + shape
	else:
		extention = ()
		extention_access = ()

	new_arr = ndarray(shape, dtype, order)
	extended_access = extention_access + (...,)
	new_arr[extended_access] = arr[...]
	return new_arr
