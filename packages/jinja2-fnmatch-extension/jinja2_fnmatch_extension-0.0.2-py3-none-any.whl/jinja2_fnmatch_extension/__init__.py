import fnmatch
import jinja2
from jinja2.ext import Extension


@jinja2.evalcontextfilter
def _fnmatch(eval_ctx, value, pattern):
    return fnmatch.fnmatch(value, pattern)


class FnMatchExtension(Extension):

    def __init__(self, environment):
        super(FnMatchExtension, self).__init__(environment)
        environment.filters['fnmatch'] = _fnmatch
