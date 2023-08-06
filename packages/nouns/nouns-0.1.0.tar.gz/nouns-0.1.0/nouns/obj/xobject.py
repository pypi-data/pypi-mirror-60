import inspect
from functools import partial

import results

from nouns.css import histo_bar

from .human import (
    decimal_places_count,
    is_iterable,
    is_mapping,
    is_none,
    is_numeric,
    is_table,
    is_text,
    pad_number,
)

ATTR_NAME = "_nouns"
ORIG = "_nouns_orig"
VAL = "_v"


def get_x():
    x = X()
    return x


def v(x):
    if is_mapping(x) and ATTR_NAME in x:
        return x[VAL]
    else:
        return x


def format_number(xvalue, dp=None):
    if dp is not None:
        return pad_number(str(xvalue), decimal_places=dp)
    else:
        v = float(xvalue)
        if v.is_integer():
            return str(int(v))
        else:
            return str(v)


def postprocess_results(t, x):
    t.annotate_histogram_amplitudes()

    klist = t.keys()

    max_decimal_places = {}

    for k in klist:
        numeric_values = [_ for _ in t[k] if is_numeric(_)]
        if numeric_values:
            max_decimal_places[k] = max(decimal_places_count(_) for _ in numeric_values)

    for s in t:
        for k in klist:
            v = s[k]

            histo = getattr(v, "histo", None)

            if is_numeric(v):
                if histo:
                    s[k] = x.number(
                        v, dp=max_decimal_places[k], _histo=histo_bar(*histo)
                    )
                else:
                    s[k] = x.number(v, dp=max_decimal_places[k])

    if not hasattr(t, "_no_hier"):
        t.make_hierarchical()


def process_text(xvalue, x, **kwargs):
    return x._x("text", xvalue, xvalue, kwargs)


def process_number(xvalue, x, dp=None, **kwargs):
    return x._x("number", xvalue, format_number(xvalue, dp), kwargs)


def process_mapping(xvalue, x):
    orig = xvalue
    if not is_mapping(xvalue):
        xvalue = {k: v for k, v in inspect.getmembers(xvalue) if not k.startswith("_")}
    keys = [x(_) for _ in xvalue.keys()]

    contents = [x(_) for _ in xvalue.values()]
    for k, c in zip(keys, contents):
        c["_key"] = k

    attrs_dict = {c["_key"][VAL]: c for c in contents}

    return x._x("mapping", orig, value=None, attrs_dict=attrs_dict)


def process_iterable(xvalue, x):
    contents = [x(_) for _ in xvalue]

    attrs_dict = {str(i): v for i, v in enumerate(contents)}
    return x._x("iterable", xvalue, value=None, attrs_dict=attrs_dict)


def process_table(xvalue, x, **kwargs):
    if isinstance(xvalue, results.Results):
        postprocess_results(xvalue, x)
    contents = process_iterable([process_mapping(row, x) for row in xvalue], x)

    if hasattr(xvalue, "keys"):
        columns = xvalue.keys()
    else:
        try:
            columns = xvalue[0].keys()
        except IndexError:
            columns = []
    extras = {"_columns": process_iterable([x(c) for c in columns], x)}
    extras.update(contents)

    # extras = None
    return x._x("table", contents, value=None, attrs_dict=extras)


def process_none(xvalue, x):
    return {ATTR_NAME: "none", ORIG: None, VAL: None}


def process_default(xvalue, x, **kwargs):
    thing = {ATTR_NAME: "default", ORIG: kwargs}

    processed_kwargs = {k: x(v) for k, v in kwargs.items()}
    thing.update(**processed_kwargs)
    return thing


class X(object):
    def __init__(self, before_hook=None):
        self.tests = [
            ("none", is_none),
            ("text", is_text),
            ("number", is_numeric),
            ("mapping", is_mapping),
            ("table", is_table),
            ("iterable", is_iterable),
        ]

        self.processors = {
            "text": process_text,
            "number": process_number,
            "mapping": process_mapping,
            "iterable": process_iterable,
            "none": process_none,
            "table": process_table,
            "default": process_default,
        }

        self.before_hook = before_hook

    def get_xtype(self, x):
        for tname, is_xtype in self.tests:
            if is_xtype(x):
                return tname

    def x(self, x=None, xtype=None, **kwargs):
        if self.before_hook:
            x = self.before_hook(x, xtype, **kwargs)

        try:
            if ATTR_NAME in x:
                return x
        except TypeError:
            pass

        if kwargs and x is None:
            processor_name = "default"
        else:
            processor_name = xtype if xtype in self.processors else self.get_xtype(x)
            if processor_name is None:
                processor_name = "mapping"

        processor = self.processors[processor_name]

        processed = processor(x, self, **kwargs)
        processed[ATTR_NAME] = xtype or processor_name
        return processed

    def _x(self, nounstype, original, value=None, attrs_dict=None):
        result = {ATTR_NAME: nounstype, ORIG: original}

        if value:
            result[VAL] = value

        if attrs_dict:
            result.update(attrs_dict)
        return result

    def __getattr__(self, name):
        return partial(self.x, xtype=name)

    def __call__(self, *args, **kwargs):
        return self.x(*args, **kwargs)
