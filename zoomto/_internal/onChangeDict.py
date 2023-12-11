import json

class OnChangeSaveDict(dict):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        super().__init__(*args, **kwargs)
        self._load()

    def _save(self):
        with open(self.filename, 'w') as f:
            json.dump(self, f)

    def _load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.update(data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._save()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self._save()

    def clear(self):
        super().clear()
        self._save()

    def pop(self, *args):
        result = super().pop(*args)
        self._save()
        return result

    def popitem(self):
        result = super().popitem()
        self._save()
        return result

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]