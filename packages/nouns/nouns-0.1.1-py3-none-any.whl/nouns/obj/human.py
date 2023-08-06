from collections import abc
from numbers import Number


def is_none(x):
    return x is None


def is_table(x):
    original = x

    if hasattr(x, "__iter__"):
        x = list(x)

    if not is_iterable(x):
        return False

    if len(x):
        for each in x:
            if not (
                callable(getattr(each, "keys", None))
                and callable(getattr(each, "values", None))
            ):
                return False

            if not list(each) == list(each.values()):
                return False
    else:
        if hasattr(original, "keys"):
            return True

        if hasattr(original, "paging"):
            return True

        return False
    return True


def is_mapping(x):
    return isinstance(x, abc.Mapping)


def is_text(x):
    return isinstance(x, str)


def is_iterable(x):
    if is_text(x):
        return False
    return isinstance(x, abc.Iterable)


def is_numeric(x):
    return isinstance(x, Number)


def is_numeric_type(t):
    return issubclass(t, Number)


def is_groupable_type(t):
    return not is_numeric_type(t)


def is_all_integers(values):
    try:
        return all(x is None or float(x).is_integer() for x in values)
    except ValueError:
        return False


def format_pgrange(x):
    return {
        "_nu": "range",
        "range": x,
        "description": "{} -> {}".format(x.lower, x.upper),
    }


def format(value, t=None, percent=False):
    t = t or type(value)

    if t.__module__ == "psycopg2._range":
        return "{} → {}".format(value.lower, value.upper)

        # TODO: More advanced formatting of edge cases:
        # with the following properties: 'isempty', 'lower', 'lower_inc', 'lower_inf', 'upper', 'upper_inc', 'upper_inf'

    if value is None:
        return "NULL"

    if percent:
        return str(round(float(value) * 100.0, 1)) + "%"

    if is_numeric(value):
        return format_number(value)
    else:
        return str(value)


def format_number(x, dp=3):
    return pad_number(str(x), dp)


def pad_number(numstring, decimal_places=3):
    DECIMAL_SEPARATOR = "."

    if decimal_places < 0:
        raise ValueError

    if decimal_places == 0:
        return numstring.rsplit(DECIMAL_SEPARATOR, 1)[0]

    else:
        has_dot = DECIMAL_SEPARATOR in numstring

        if has_dot:
            numstring = numstring.rstrip("0")

        dp = decimal_places_count(numstring)

        if not has_dot:
            numstring += DECIMAL_SEPARATOR

        hidden = ""

        if dp == 0:
            numstring = numstring.replace(DECIMAL_SEPARATOR, "")

            hidden += DECIMAL_SEPARATOR

        shortage = decimal_places - dp

        hidden += "0" * shortage
        if hidden:
            numstring += "<span>" + hidden + "</span>"
        return numstring


def decimal_places_count(numstring):
    if not isinstance(numstring, str):
        numstring = str(numstring)
    DECIMAL_SEPARATOR = "."

    try:
        before, after = numstring.split(DECIMAL_SEPARATOR)
    except ValueError:
        return 0
    without_trailing_zeroes = after.rstrip("0")
    return len(without_trailing_zeroes)
