# BSD 3-Clause License; see https://github.com/jpivarski/awkward-1.0/blob/master/LICENSE

import operator

import numpy
import numba

import awkward1.layout
from ..._numba import cpu, util, content

@numba.extending.typeof_impl.register(awkward1.layout.EmptyArray)
def typeof(val, c):
    return EmptyArrayType(numba.typeof(val.identities), util.dict2parameters(val.parameters))

class EmptyArrayType(content.ContentType):
    def __init__(self, identitiestpe, parameters):
        assert isinstance(parameters, tuple)
        super(EmptyArrayType, self).__init__(name="ak::EmptyArrayType(identities={0}, parameters={1})".format(identitiestpe.name, util.parameters2str(parameters)))
        self.identitiestpe = identitiestpe
        self.parameters = parameters

    @property
    def ndim(self):
        return 1

    def getitem_int(self):
        raise ValueError("cannot compile getitem for EmptyArray, which has unknown element type")

    def getitem_range(self):
        return self

    def getitem_str(self):
        raise IndexError("cannot slice EmptyArray with str (Record field name)")

    def getitem_tuple(self, wheretpe):
        if len(wheretpe.types) == 0:
            return self
        elif len(wheretpe.types) == 1 and isinstance(wheretpe.types[0], numba.types.SliceType):
            return self
        else:
            raise ValueError("cannot compile getitem for EmptyArray, which has unknown element type")

    def getitem_next(self, wheretpe, isadvanced):
        if len(wheretpe.types) == 0:
            return self
        else:
            raise ValueError("cannot compile getitem for EmptyArray, which has unknown element type")

    def carry(self):
        return self

    @property
    def lower_len(self):
        return lower_len

    @property
    def lower_getitem_nothing(self):
        return lower_getitem_nothing

    @property
    def lower_getitem_range(self):
        return lower_getitem_range

    @property
    def lower_getitem_next(self):
        return lower_getitem_next

    @property
    def lower_carry(self):
        return lower_carry

@numba.extending.register_model(EmptyArrayType)
class EmptyArrayModel(numba.datamodel.models.StructModel):
    def __init__(self, dmm, fe_type):
        members = []
        if fe_type.identitiestpe != numba.none:
            members.append(("identities", fe_type.identitiestpe))
        super(EmptyArrayModel, self).__init__(dmm, fe_type, members)

@numba.extending.unbox(EmptyArrayType)
def unbox(tpe, obj, c):
    proxyout = numba.cgutils.create_struct_proxy(tpe)(c.context, c.builder)
    if tpe.identitiestpe != numba.none:
        id_obj = c.pyapi.object_getattr_string(obj, "identities")
        proxyout.identities = c.pyapi.to_native_value(tpe.identitiestpe, id_obj).value
        c.pyapi.decref(id_obj)
    is_error = numba.cgutils.is_not_null(c.builder, c.pyapi.err_occurred())
    return numba.extending.NativeValue(proxyout._getvalue(), is_error)

@numba.extending.box(EmptyArrayType)
def box(tpe, val, c):
    EmptyArray_obj = c.pyapi.unserialize(c.pyapi.serialize_object(awkward1.layout.EmptyArray))
    proxyin = numba.cgutils.create_struct_proxy(tpe)(c.context, c.builder, value=val)
    args = []
    if tpe.identitiestpe != numba.none:
        args.append(c.pyapi.from_native_value(tpe.identitiestpe, proxyin.identities, c.env_manager))
    else:
        args.append(c.pyapi.make_none())
    args.append(util.parameters2dict_impl(c, tpe.parameters))
    out = c.pyapi.call_function_objargs(EmptyArray_obj, args)
    for x in args:
        c.pyapi.decref(x)
    c.pyapi.decref(EmptyArray_obj)
    return out

@numba.extending.lower_builtin(len, EmptyArrayType)
def lower_len(context, builder, sig, args):
    return context.get_constant(numba.intp, 0)

def lower_getitem_nothing(context, builder, tpe, val):
    return val

@numba.extending.lower_builtin(operator.getitem, EmptyArrayType, numba.types.slice2_type)
def lower_getitem_range(context, builder, sig, args):
    rettpe, (tpe, wheretpe) = sig.return_type, sig.args
    val, whereval = args
    if context.enable_nrt:
        context.nrt.incref(builder, rettpe, val)
    return val

@numba.extending.lower_builtin(operator.getitem, EmptyArrayType, numba.types.BaseTuple)
def lower_getitem_tuple(context, builder, sig, args):
    rettpe, (tpe, wheretpe) = sig.return_type, sig.args
    val, whereval = args
    if context.enable_nrt:
        context.nrt.incref(builder, rettpe, val)
    return val

def lower_getitem_next(context, builder, arraytpe, wheretpe, arrayval, whereval, advanced):
    if context.enable_nrt:
        context.nrt.incref(builder, arraytpe, arrayval)
    return arrayval

def lower_carry(context, builder, arraytpe, carrytpe, arrayval, carryval):
    if context.enable_nrt:
        context.nrt.incref(builder, arraytpe, arrayval)
    return arrayval

@numba.typing.templates.infer_getattr
class type_methods(numba.typing.templates.AttributeTemplate):
    key = EmptyArrayType

    def generic_resolve(self, tpe, attr):
        if attr == "identities":
            if tpe.identitiestpe == numba.none:
                return numba.optional(identity.IdentitiesType(numba.int32[:, :]))
            else:
                return tpe.identitiestpe

@numba.extending.lower_getattr(EmptyArrayType, "identities")
def lower_identities(context, builder, tpe, val):
    proxyin = numba.cgutils.create_struct_proxy(tpe)(context, builder, value=val)
    if tpe.identitiestpe == numba.none:
        return context.make_optional_none(builder, identity.IdentitiesType(numba.int32[:, :]))
    else:
        if context.enable_nrt:
            context.nrt.incref(builder, tpe.identitiestpe, proxyin.identities)
        return proxyin.identities
