import logging

from batchout.core.config import with_config_key
from batchout.core.registry import Registry
from batchout.core.data import Data
from batchout.selectors import Selector

log = logging.getLogger(__name__)


class MappingSelectorConfigInvalid(Exception):
    pass


@with_config_key('fields', raise_exc=MappingSelectorConfigInvalid)
@Registry.bind(Selector, 'mapping')
class MappingSelector(Selector):

    def __init__(self, config):
        self.set_fields(config)
        if not isinstance(self._fields, dict):
            raise MappingSelectorConfigInvalid('mapping expected for fields')

    def apply(self, data):
        dst_cols, src_cols = list(self._fields.keys()), list(self._fields.values())
        result = Data(*dst_cols)
        for src_name in data.sources:
            for row in data.rows(src_name):
                rec = dict(zip(data.columns, row))
                result.with_row(*[rec[col] for col in src_cols])
        return result
