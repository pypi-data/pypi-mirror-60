import warnings

from results import resource_path

from .obj import get_x  # noqa
from .templates import NounsTemplate, Templates  # noqa

warnings.simplefilter("ignore", category=DeprecationWarning)

BUILTIN_TEMPLATES_FOLDER = resource_path("builtin_templates")


def template(thing, t=None):
    x = get_x()

    _t = Templates(preprocess=x, folders=[BUILTIN_TEMPLATES_FOLDER])

    if t:
        _t.templates["thing"] = NounsTemplate(t)
        return _t.render(x.thing(thing))
    else:
        return _t.render(x(thing))
