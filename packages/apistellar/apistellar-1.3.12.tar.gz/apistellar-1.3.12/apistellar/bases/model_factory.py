# 过时
from .metas import ModelFactoryMeta
from .components import Component


class ModelFactory(Component, metaclass=ModelFactoryMeta):
    model = object

    async def product(self, *args, **kwargs):
        pass
