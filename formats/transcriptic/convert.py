import sys
from ..converter import Converter, ConversionError, ValidationError
from .runner import convert_transcriptic

class Transcriptic(Converter):
    def convert(self, input_fp, output_fp=None, verbose=True, config={}, enforce_validation=True):
        # The convert_FORMAT runners are relatively indepdent scripts
        # but we need to pass in config options sometimes in order to
        # set up service and database lookups. This establishes config
        # priority as such:
        # 1. If config is passed to Transcriptic.convert, use that, else
        # 2. If config was passed when constructing Transcript() use it, else
        # 3. Use an empty dict for config
        passed_config = self.options
        if config != {}:
            passed_config = config
        return convert_transcriptic(self.targetschema, input_fp, verbose=verbose, config=passed_config, output_file=output_fp, enforce_validation=enforce_validation)

