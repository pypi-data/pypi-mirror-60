import six


def essence(attrs, mutable=True):

    if isinstance(attrs, six.string_types):
        attrs = attrs.split(' ')

    def essence_maker(cls):

        def __essence__(self):
            return tuple(getattr(self, attr) for attr in attrs)

        setattr(cls, '__essence__', __essence__)

        def eq(self, other):
            if isinstance(other, cls):
                return self.__essence__() == cls.__essence__(other)
            return NotImplemented

        setattr(cls, '__eq__', eq)

        if six.PY2:

            # Taken from:
            #   https://stackoverflow.com/a/35781654
            def ne(self, other):
                equal = self.__eq__(other)
                return equal if equal is NotImplemented else not equal

            setattr(cls, '__ne__', ne)

        def hash_(self):
            return hash(self.__essence__())

        setattr(cls, '__hash__', None if mutable else hash_)

        # Would use total_ordering, but the recursive comparison issue is still present in
        # Python 2.7, so have to work this way instead.
        def lt(self, other):
            if isinstance(other, cls):
                return self.__essence__() < cls.__essence__(other)
            return NotImplemented

        def le(self, other):
            if isinstance(other, cls):
                return self.__essence__() <= cls.__essence__(other)
            return NotImplemented

        def gt(self, other):
            if isinstance(other, cls):
                return self.__essence__() > cls.__essence__(other)
            return NotImplemented

        def ge(self, other):
            if isinstance(other, cls):
                return self.__essence__() >= cls.__essence__(other)
            return NotImplemented

        setattr(cls, '__lt__', lt)
        setattr(cls, '__le__', le)
        setattr(cls, '__gt__', gt)
        setattr(cls, '__ge__', ge)
        return cls

    return essence_maker


def described(inner):

    def described_maker(cls):

        def repr_(self):
            return ('<{0.__class__.__name__} ' + inner + '>').format(self)

        setattr(cls, '__repr__', repr_)

        if '__str__' not in cls.__dict__:
            def str_(self):
                return repr(self)
            setattr(cls, '__str__', str_)

        return six.python_2_unicode_compatible(cls)

    return described_maker


class AttrItems(object):

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)
        except TypeError:
            if isinstance(key, int):
                raise KeyError(key)
            raise

    def __setitem__(self, key, value):
        try:
            setattr(self, key, value)
        except AttributeError:
            raise KeyError(key)

    def __delitem__(self, key):
        try:
            delattr(self, key)
        except AttributeError:
            raise KeyError(key)


class ItemAttrs(object):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        try:
            self[name] = value
        except KeyError:
            raise AttributeError(name)

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


class MappingNS(ItemAttrs):

    def __repr__(self):
        keys = sorted(self)
        items = ("{}={!r}".format(k, self[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __str__(self):
        return repr(self)

    def __dir__(self):
        superdir = getattr(super(MappingNS, self), '__dir__', None)
        if superdir is not None:
            sdir = superdir()  # pylint: disable=not-callable
        else:
            sdir = dir(type(self)) + list(getattr(self, '__dict__', {}))
        return sdir + list(self)


try:
    from types import SimpleNamespace as Namespace
except ImportError:
    from argparse import Namespace


class attrdict(ItemAttrs, dict):
    pass


class nsdict(MappingNS, dict):
    pass


class nsmap(Namespace, AttrItems):
    pass


del Namespace


def deep_remap(struct, newtype, maptypes=(dict,), seqtypes=(tuple, list)):
    if isinstance(struct, maptypes):
        res = newtype()
        for k, v in struct.items():
            res[k] = deep_remap(v, newtype, maptypes, seqtypes)
        return res

    if isinstance(struct, seqtypes):
        return type(struct)(deep_remap(x, newtype, maptypes, seqtypes) for x in struct)

    return struct


def attrcopy(source, attrs_to_get, maptype=nsdict):
    res = maptype()
    for attrspec in reversed(sorted(attrs_to_get, key=len)):
        _attrcopy(res, source, attrspec.split('.'), maptype)
    return res


def _attrcopy(res, source, attrspec, maptype=dict):
    thisattr = attrspec[0]

    # Just copy this attribute.
    if len(attrspec) == 1:
        # If it's already known to us, then don't set it.
        # This probably implies its a namespace with attributes inside.
        if thisattr not in res:
            res[thisattr] = getattr(source, thisattr)
        return

    # Work out if are going to be dealing with a sequence.
    innertype = None
    if thisattr[-2:] in ['[]']:
        thisattr, innertype = thisattr[:-2], thisattr[-2:]

    # Navigate down into the next object.
    value = getattr(source, thisattr)
    attrspec = attrspec[1:]

    # Prepare the container object we're going to put writing into.
    if thisattr not in res:
        if innertype == '[]':
            res[thisattr] = type(value)(maptype() for _ in value)
        else:
            res[thisattr] = maptype()

    newres = res[thisattr]

    # Recurse our way downwards.
    if innertype == '[]':
        for nres, s in zip(newres, value):
            _attrcopy(nres, s, attrspec, maptype)
    else:
        _attrcopy(newres, value, attrspec, maptype)
