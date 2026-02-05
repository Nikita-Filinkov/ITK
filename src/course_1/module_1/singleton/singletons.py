from src.module_1.singleton.singleton_for_import import set_attr as set_attr_1
from src.module_1.singleton.singleton_for_import import get as get_2
from src.module_1.singleton.singleton_for_import import get_all as get_all_1
from src.module_1.singleton.singleton_for_import import get_all as get_all_2


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class ConfigMeta(metaclass=SingletonMeta):
    def __init__(self):
        self.config = {}

    def get(self, key):
        return self.config.get(key)

    def set_attr(self, key, value):
        self.config[key] = value
        return self.config[key]


class ConfigNew:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.config = {}

    def get(self, key):
        return self.config.get(key)

    def set_attr(self, key, value):
        self.config[key] = value
        return self.config[key]


if __name__ == "__main__":
    config_meta_1 = ConfigMeta()
    config_meta_1.set_attr("key1", 1)

    config_meta_2 = ConfigMeta()
    assert config_meta_1 is config_meta_2
    assert config_meta_1.get("key1") == config_meta_2.get("key1")

    config_new_1 = ConfigNew()
    config_new_1.set_attr("key1", 1)

    config_new_2 = ConfigNew()
    assert config_new_1 is config_new_2
    assert config_new_1.get("key1") == config_new_2.get("key1")

    set_attr_1("key1", 1)
    assert get_all_1() is get_all_2()
    assert get_2("key1") == 1
