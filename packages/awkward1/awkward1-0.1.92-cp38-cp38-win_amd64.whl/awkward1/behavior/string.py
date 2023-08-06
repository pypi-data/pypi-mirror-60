# BSD 3-Clause License; see https://github.com/jpivarski/awkward-1.0/blob/master/LICENSE

import codecs

import numpy

import awkward1.highlevel

class CharBehavior(awkward1.highlevel.Array):
    def __bytes__(self):
        return numpy.asarray(self.layout).tostring()

    def __str__(self):
        encoding = self.layout.type.parameters.get("encoding")
        if encoding is None:
            return str(self.__bytes__())
        else:
            return self.__bytes__().decode(encoding, "surrogateescape")

    def __repr__(self):
        encoding = self.layout.type.parameters.get("encoding")
        if encoding is None:
            return repr(self.__bytes__())
        else:
            return repr(self.__bytes__().decode(encoding, "surrogateescape"))

    def __iter__(self):
        for x in str(self):
            yield x

awkward1.classes["char"] = CharBehavior
byte = awkward1.layout.PrimitiveType("uint8", {"__class__": "char", "__typestr__": "byte", "encoding": None})
utf8 = awkward1.layout.PrimitiveType("uint8", {"__class__": "char", "__typestr__": "utf8", "encoding": "utf-8"})

class StringBehavior(awkward1.highlevel.Array):
    def __iter__(self):
        if self.layout.type.type.parameters.get("encoding") is None:
            for x in super(StringBehavior, self).__iter__():
                yield x.__bytes__()
        else:
            for x in super(StringBehavior, self).__iter__():
                yield x.__str__()

    def __eq__(self, other):
        raise NotImplementedError("return one boolean per string, not lists of booleans per character")

awkward1.classes["string"] = StringBehavior
bytestring = awkward1.layout.ListType(byte, {"__class__": "string", "__typestr__": "bytes"})
string = awkward1.layout.ListType(utf8, {"__class__": "string", "__typestr__": "string"})

def string_equal(one, two):
    # FIXME: this needs a much better implementation;
    # It's here just to demonstrate overloading.

    counts1 = numpy.asarray(one.count())
    counts2 = numpy.asarray(two.count())
    counts_equal = (counts1 == counts2)
    contents_equal = numpy.empty_like(counts_equal)
    for i, (x, y) in enumerate(zip(one, two)):
        contents_equal[i] = numpy.array_equal(numpy.asarray(x), numpy.asarray(y))

    return awkward1.layout.NumpyArray(counts_equal & contents_equal)

awkward1.functions[numpy.equal, "string", "string"] = string_equal
