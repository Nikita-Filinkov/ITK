class _Config:
    def __init__(self):
        self.config = {}

    def get(self, key):
        return self.config.get(key)

    def set_attr(self, key, value):
        self.config[key] = value
        return self.config[key]

    def get_all(self):
        return self.config


_config = _Config()


def get(key):
    return _config.config.get(key)


def set_attr(key, value):
    _config.config[key] = value
    return _config.config[key]


def get_all():
    return _config.config
