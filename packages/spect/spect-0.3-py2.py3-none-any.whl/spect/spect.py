import re, functools
from pprint import pformat


class Spect(object):
    """Categorize members of an object.

    Examples:
        >>> import re
        >>> repsect = Spect(re)  # The pun is strong in that one
        >>> '__doc__' in respect.dunder
        True
        >>> 'match' in respect.regular
        True
    """

    upper = re.compile(r"^[_0-9]*[A-Z][A-Z0-9_]*$")
    categorizer = re.compile(
        r"(?P<dunder>^__\w+__$)|"
        r"(?P<superprivate>^__\w+$)|"
        r"(?P<private>^_\w+$)|"
        r"(?P<alias>^[a-zA-Z]\w*_$)|"
        r"(?P<regular>^[a-zA-Z]\w*$)"
    )
    categories = list(categorizer.groupindex.keys()) + ["magic", "general"]

    def __init__(self, obj):
        self.obj = obj
        self.dir = set(dir(obj))

        self.__dict__.update({k: set() for k in self.categories})

        for mem in map(self.categorizer.match, self.dir):
            category = mem.lastgroup
            self.__dict__[category].add(mem.group(category))

        self.magic = set(filter(lambda x: callable(getattr(obj, x)), self.dunder))
        self.const = set(filter(self.upper.match, self.dir))
        self.general = self.regular  # Salute to the private & superprivate

    def __getattr__(self, attr):
        components = attr.split("_")
        if any(c not in self.categories + ["const"] for c in components):
            raise AttributeError(
                "'{}' has no attribute '{}'".format(self.__class__.__name__, attr)
            )
        const = self.const if "const" in components else self.dir
        components = [self.__dict__[x] for x in components if x != "const"]
        union = functools.reduce(lambda r, l: r | l, components)
        return union & const

    def __repr__(self):
        data = {
            k: self.__dict__[k]
            for k in self.categories
            if k != "general" and self.__dict__[k]
        }
        return "{} ({}) attributes:\n{}".format(
            self.obj.__name__, self.obj.__class__.__name__, pformat(data, compact=True)
        )


if __name__ == "__main__":
    print('Basic tests...')
    sre = Spect(re)
    assert '__doc__' in sre.dunder
    assert 'match' in sre.regular
    assert '_MAXCACHE' in sre.const_private
    assert sre.const - sre.regular == {'_MAXCACHE'}
    assert '__getattr__' in Spect(sre).magic
    print(repr(sre))
    print('Done.')
