from .converter import ConversionError
from .transcriptic import Transcriptic
from .ginkgo import Ginkgo
from .biofab import Biofab


class NoClassifierError(ConversionError):
    pass

def get_converter(json_filepath, options={}):

    try:
        t = Transcriptic(options=options)
        t.validate_input(json_filepath)
        return t
    except Exception:
        pass

    try:
        g = Ginkgo(options=options)
        g.validate_input(json_filepath)
        return g
    except Exception:
        pass

    try:
        b = Biofab(options=options)
        b.validate_input(json_filepath)
        return b
    except Exception:
        pass

    raise NoClassifierError('Classification failed for {}'.format(json_filepath))

