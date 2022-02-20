from statham.schema.constants import NotPassed
from statham.schema.elements import Object


class PropertyExtension(object):
    def get_properties(self):
        return []


class CardItemExt(PropertyExtension):
    @property
    def name(self):
        return list(self._dict.keys())[0]

    @property
    def actions(self):
        return self._dict[self.name]['actions']

    @property
    def flavour(self):
        return self._dict[self.name]['flavour']

    @property
    def tags(self):
        return self._dict[self.name]['tags']

    def get_properties(self):
        return ["name", "actions", "flavour", "tags"]


class KVBase(object):
    @property
    def key(self):
        return list(self._dict.keys())[0]

    @property
    def value(self):
        return self._dict[self.key]

    def to_obj_supplement(self, obj):
        if self.key in obj or self.value == NotPassed():
            return obj
        obj[self.key] = self.value
        return obj


class YamlDump(Object):

    def _val_to_obj(self, val):
        # Hack to avoid cyclic dependency
        if type(val).__name__ == "Cards":
            val = val
        elif isinstance(val, YamlDump):
            val = val.to_obj()
        elif isinstance(val, list):
            v = []
            for i in val:
                v.append(self._val_to_obj(i))
            val = v

        elif isinstance(val, dict):
            nv = {}
            for k, v in val.items():
                nv[k] = self._val_to_obj(v)
            val = nv

        return val

    def to_obj(self):
        obj = {}
        props = list(self._properties)
        if isinstance(self, PropertyExtension):
            props.extend(self.get_properties())
        for key in props:
            val = getattr(self, key)
            if val is None or val == NotPassed():
                continue
            obj[key] = self._val_to_obj(val)

        if isinstance(self, KVBase):
            self.to_obj_supplement(obj)

        return obj
