# BSD 3-Clause License; see https://github.com/jpivarski/awkward-1.0/blob/master/LICENSE

import sys

import numpy
import numba
import llvmlite.ir.types
import llvmlite.llvmpy.core

from .._numba import cpu

py27 = (sys.version_info[0] < 3)

if not py27:
    exec("""
def debug(context, builder, *args):
    assert len(args) % 2 == 0
    tpes, vals = args[0::2], args[1::2]
    context.get_function(print, numba.none(*tpes))(builder, tuple(vals))
""", globals())

dynamic_addrs = {}
def globalstring(context, builder, pyvalue):
    if pyvalue not in dynamic_addrs:
        buf = dynamic_addrs[pyvalue] = numpy.array(pyvalue.encode("utf-8") + b"\x00")
        context.add_dynamic_addr(builder, buf.ctypes.data, info="str({0})".format(repr(pyvalue)))
    ptr = context.get_constant(numba.types.uintp, dynamic_addrs[pyvalue].ctypes.data)
    return builder.inttoptr(ptr, llvmlite.llvmpy.core.Type.pointer(llvmlite.llvmpy.core.Type.int(8)))

RefType = numba.int64

index8tpe = numba.types.Array(numba.int8, 1, "C")
indexU8tpe = numba.types.Array(numba.uint8, 1, "C")
index32tpe = numba.types.Array(numba.int32, 1, "C")
indexU32tpe = numba.types.Array(numba.uint32, 1, "C")
index64tpe = numba.types.Array(numba.int64, 1, "C")
def indextpe(indexname):
    if indexname == "64":
        return index64tpe
    elif indexname == "32":
        return index32tpe
    elif indexname == "U32":
        return indexU32tpe
    elif indexname == "8":
        return index8tpe
    elif indexname == "U8":
        return indexU8tpe
    else:
        raise AssertionError("unrecognized index type: {0}".format(indexname))

def cast(context, builder, fromtpe, totpe, val):
    if isinstance(fromtpe, llvmlite.ir.types.IntType):
        if fromtpe.width == 8:
            fromtpe = numba.int8
        elif fromtpe.width == 16:
            fromtpe = numba.int16
        elif fromtpe.width == 32:
            fromtpe = numba.int32
        elif fromtpe.width == 64:
            fromtpe = numba.int64
        else:
            raise AssertionError("unrecognized bitwidth")
    if fromtpe.bitwidth < totpe.bitwidth:
        return builder.sext(val, context.get_value_type(totpe))
    elif fromtpe.bitwidth > totpe.bitwidth:
        return builder.trunc(val, context.get_value_type(totpe))
    else:
        return val

def arrayptr(context, builder, tpe, val):
    return numba.targets.arrayobj.make_array(tpe)(context, builder, val).data

def arraylen(context, builder, tpe, val, totpe=None):
    if isinstance(tpe, numba.types.Array):
        out = numba.targets.arrayobj.array_len(context, builder, numba.intp(tpe), (val,))
    else:
        out = tpe.lower_len(context, builder, numba.intp(tpe), (val,))
    if totpe is None:
        return out
    else:
        return cast(context, builder, numba.intp, totpe, out)

def call(context, builder, fcn, args, errormessage=None):
    fcntpe = context.get_function_pointer_type(fcn.numbatpe)
    fcnval = context.add_dynamic_addr(builder, fcn.numbatpe.get_pointer(fcn), info=fcn.name)
    fcnptr = builder.bitcast(fcnval, fcntpe)

    err = context.call_function_pointer(builder, fcnptr, args)

    if fcn.restype is cpu.Error:
        assert errormessage is not None, "this function can return an error"
        proxyerr = numba.cgutils.create_struct_proxy(cpu.Error.numbatpe)(context, builder, value=err)
        with builder.if_then(builder.icmp_signed("!=", proxyerr.str, context.get_constant(numba.intp, 0)), likely=False):
            context.call_conv.return_user_exc(builder, ValueError, (errormessage,))

def newindex8(context, builder, lentpe, lenval):
    return numba.targets.arrayobj.numpy_empty_nd(context, builder, index8tpe(lentpe), (lenval,))
def newindexU8(context, builder, lentpe, lenval):
    return numba.targets.arrayobj.numpy_empty_nd(context, builder, indexU8tpe(lentpe), (lenval,))
def newindex32(context, builder, lentpe, lenval):
    return numba.targets.arrayobj.numpy_empty_nd(context, builder, index32tpe(lentpe), (lenval,))
def newindexU32(context, builder, lentpe, lenval):
    return numba.targets.arrayobj.numpy_empty_nd(context, builder, indexU32tpe(lentpe), (lenval,))
def newindex64(context, builder, lentpe, lenval):
    return numba.targets.arrayobj.numpy_empty_nd(context, builder, index64tpe(lentpe), (lenval,))
def newindex(indexname, context, builder, lentpe, lenval):
    if indexname == "64":
        return newindex64(context, builder, lentpe, lenval)
    elif indexname == "32":
        return newindex32(context, builder, lentpe, lenval)
    elif indexname == "U32":
        return newindexU32(context, builder, lentpe, lenval)
    elif indexname == "8":
        return newindex8(context, builder, lentpe, lenval)
    elif indexname == "U8":
        return newindexU8(context, builder, lentpe, lenval)
    else:
        raise AssertionError("unrecognized index type: {0}".format(indexname))

@numba.jit(nopython=True)
def shapeat(shapeat, array, at, ndim):
    redat = at - (ndim - array.ndim)
    if redat < 0:
        return 1
    elif shapeat == 0:
        return 0
    elif shapeat == 1:
        return array.shape[redat]
    elif shapeat == array.shape[redat] or array.shape[redat] == 1:
        return shapeat
    else:
        raise ValueError("cannot broadcast arrays to the same shape")

@numba.generated_jit(nopython=True)
def broadcast_to(array, shape):
    if isinstance(array, numba.types.Array):
        def impl(array, shape):
            out = numpy.empty(shape, array.dtype)
            out[:] = array
            return out
        return impl
    elif isinstance(array, numba.types.Integer):
        def impl(array, shape):
            return numpy.full(shape, array, numpy.int64)
        return impl
    else:
        return lambda array, shape: array

@numba.generated_jit(nopython=True)
def broadcast_arrays(arrays):
    if not isinstance(arrays, numba.types.BaseTuple) or not any(isinstance(x, numba.types.Array) for x in arrays.types):
        return lambda arrays: arrays

    else:
        ndim = max(t.ndim if isinstance(t, numba.types.Array) else 1 for t in arrays.types)
        def getshape(i, at):
            if i == -1:
                return "1"
            elif isinstance(arrays.types[i], numba.types.Array):
                return "shapeat({0}, arrays[{1}], {2}, {3})".format(getshape(i - 1, at), i, at, ndim)
            else:
                return getshape(i - 1, at)
        g = {"shapeat": shapeat, "broadcast_to": broadcast_to}
        exec("""
def impl(arrays):
    shape = ({0})
    return ({1})
""".format(" ".join(getshape(len(arrays.types) - 1, at) + "," for at in range(ndim)),
           " ".join("broadcast_to(arrays[{0}], shape),".format(at) if isinstance(arrays.types[at], (numba.types.Array, numba.types.Integer)) else "arrays[{0}],".format(at) for at in range(len(arrays.types)))), g)
        return g["impl"]

def typing_broadcast_arrays(arrays):
    if not isinstance(arrays, numba.types.BaseTuple) or not any(isinstance(x, numba.types.Array) for x in arrays.types):
        return arrays
    else:
        return numba.types.Tuple([numba.types.Array(numba.int64, 1, "C") if isinstance(t, numba.types.Integer) else t for t in arrays.types])

@numba.generated_jit(nopython=True)
def regularize_slice(arrays):
    if not isinstance(arrays, numba.types.BaseTuple) and isinstance(arrays, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(arrays.dtype, numba.types.Boolean):
        return lambda arrays: numpy.nonzero(arrays)

    elif not isinstance(arrays, numba.types.BaseTuple) or not any(isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) for t in arrays.types):
        return lambda arrays: arrays

    else:
        code = "def impl(arrays):\n"
        indexes = []   # all entries have trailing commas to ensure output is a tuple
        for i, t in enumerate(arrays.types):
            if isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(t.dtype, numba.types.Boolean):
                code += "    x{0} = numpy.nonzero(arrays[{1}])\n".format(i, i)
                indexes.extend(["x{0}[{1}],".format(i, j) for j in range(arrays.types[i].ndim)])
            elif isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(t.dtype, numba.types.Integer):
                indexes.append("numpy.asarray(arrays[{0}], numpy.int64),".format(i))
            elif isinstance(t, (numba.types.ArrayCompatible, numba.types.List)):
                raise TypeError("arrays must have boolean or integer type")
            else:
                indexes.append("arrays[{0}],".format(i))
        code += "    return ({0})".format(" ".join(indexes))
        g = {"numpy": numpy}
        exec(code, g)
        return g["impl"]

def typing_regularize_slice(arrays):
    out = ()
    if not isinstance(arrays, numba.types.BaseTuple) and isinstance(arrays, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(arrays.dtype, numba.types.Boolean):
        return numba.types.Tuple(arrays.ndims*(numba.types.Array(numba.int64, 1, "C"),))

    elif not isinstance(arrays, numba.types.BaseTuple) or not any(isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) for t in arrays.types):
        return arrays

    else:
        for t in arrays.types:
            if isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(t.dtype, numba.types.Boolean):
                out = out + t.ndims*(numba.types.Array(numba.int64, 1, "C"),)
            elif isinstance(t, (numba.types.ArrayCompatible, numba.types.List)) and isinstance(t.dtype, numba.types.Integer):
                out = out + (numba.types.Array(numba.int64, 1, "C"),)
            elif isinstance(t, (numba.types.ArrayCompatible, numba.types.List)):
                raise TypeError("arrays must have boolean or integer type")
            else:
                out = out + (t,)
        return numba.types.Tuple(out)

def preprocess_slicetuple(context, builder, wheretpe, whereval):
    wheretpe2 = typing_regularize_slice(wheretpe)
    regularize_slice.compile(wheretpe2(wheretpe))
    cres = regularize_slice.overloads[(wheretpe,)]
    whereval2 = context.call_internal(builder, cres.fndesc, wheretpe2(wheretpe), (whereval,))

    wheretpe3 = typing_broadcast_arrays(wheretpe2)
    broadcast_arrays.compile(wheretpe3(wheretpe2))
    cres2 = broadcast_arrays.overloads[(wheretpe2,)]
    whereval3 = context.call_internal(builder, cres2.fndesc, wheretpe3(wheretpe2), (whereval2,))

    return wheretpe3, whereval3

def preserves_type(slice, isadvanced):
    if isinstance(slice, numba.types.Integer):
        return False
    elif isinstance(slice, numba.types.SliceType):
        return True
    elif isinstance(slice, numba.types.EllipsisType):
        return True
    elif isinstance(slice, type(numba.typeof(numpy.newaxis))):
        return False
    elif isinstance(slice, (numba.types.Array, numba.types.List, numba.types.ArrayCompatible)):
        return not isadvanced
    elif isinstance(slice, numba.types.StringLiteral):
        return False
    else:
        raise AssertionError(slice)

def dict2parameters(parameters):
    return tuple(sorted(parameters.items()))

def parameters2str(parameters):
    return "{" + ", ".join("{0}: {1}".format(n, x) for n, x in parameters) + "}"

def parameters2dict_impl(c, parameters):
    dict_obj = c.pyapi.unserialize(c.pyapi.serialize_object(dict))
    parameters_obj = c.pyapi.unserialize(c.pyapi.serialize_object(parameters))
    out = c.pyapi.call_function_objargs(dict_obj, (parameters_obj,))
    c.pyapi.decref(dict_obj)
    c.pyapi.decref(parameters_obj)
    return out
