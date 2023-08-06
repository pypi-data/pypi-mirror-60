import json
import asyncio

from abc import ABCMeta
from collections.abc import Mapping, MutableMapping

from apistar.exceptions import ConfigurationError, ValidationError

from . import validators
from ..persistence import PersistentMeta
from ..helper import TypeEncoder, add_success_callback


class TypeMetaclass(ABCMeta):

    def __new__(mcs, name, bases, attrs):
        properties = []
        for key, value in list(attrs.items()):
            if key in ['keys', 'items', 'values', 'get', "clear",
                       'validator', "setdefault", "pop", "popitem"]:
                msg = (
                    'Cannot use reserved name "%s" on Type "%s", as it '
                    'clashes with the class interface.'
                )
                raise ConfigurationError(msg % (key, name))

            elif hasattr(value, 'validate'):
                attrs.pop(key)
                properties.append((key, value))

        # If this class is subclassing another Type, add that Type's properties.
        # Note that we loop over the bases in reverse. This is necessary in order
        # to maintain the correct order of properties.
        for base in reversed(bases):
            if hasattr(base, 'validator'):
                properties = [
                    (key, base.validator.properties[key]) for key
                    in base.validator.properties
                    if key not in attrs
                ] + properties

        properties = sorted(
            properties,
            key=lambda item: item[1]._creation_counter
        )

        required = [
            key for key, value in properties
            if not value.has_default()
        ]
        attrs['_creation_counter'] = validators.Validator._creation_counter
        validators.Validator._creation_counter += 1
        cls = super(TypeMetaclass, mcs).__new__(mcs, name, bases, attrs)

        cls.validator = validators.Object(
            def_name=name,
            properties=properties,
            required=required,
            additional_properties=None,
            model=cls
        )

        return cls

    def __subclasscheck__(self, subclass):
        """
        3.7.3 abc __subclasscheck__ 被抽象到builtin模块中，当subclass为非类时会报错：
        TypeError: issubclass() arg 1 must be a class
        :param subclass:
        :return:
        """
        try:
            return super(TypeMetaclass, self).__subclasscheck__(subclass)
        except TypeError:
            return False


class Type(MutableMapping, metaclass=TypeMetaclass):

    def __init__(self, *args, **kwargs):
        definitions = None
        allow_coerce = False
        force_format = False

        if args:
            assert len(args) == 1
            definitions = kwargs.pop('definitions', definitions)
            allow_coerce = kwargs.pop('allow_coerce', allow_coerce)
            force_format = kwargs.pop('force_format', force_format)
            assert not kwargs

            if args[0] is None or isinstance(args[0], (str, bytes, bool, int, float, list)):
                raise ValidationError('Must be an object.')
            elif isinstance(args[0], Mapping):
                # Instantiated with a dict.
                value = args[0]
            else:
                # Instantiated with an object instance.
                value = {}
                for key, val in self.validator.properties.items():
                    v = getattr(args[0], key, validators.NO_DEFAULT)
                    if v != validators.NO_DEFAULT:
                        value[key] = v
        else:
            # Instantiated with keyword arguments.
            value = kwargs
        object.__setattr__(self, 'allow_coerce', allow_coerce)
        object.__setattr__(self, '_dict', dict(value))
        object.__setattr__(self, 'formatted', False)

        if force_format:
            self.format(self.allow_coerce)

    def format(self, allow_coerce=False):
        object.__setattr__(self, 'allow_coerce', allow_coerce)
        if not self.formatted:
            object.__setattr__(self, '_dict', self.validator.validate(
                self._dict, allow_coerce=self.allow_coerce))
            object.__setattr__(self, 'formatted', True)

    @classmethod
    def validate(cls, value, definitions=None, allow_coerce=False, force_format=True):
        return cls(value,
                   definitions=definitions,
                   allow_coerce=allow_coerce,
                   force_format=force_format)

    def __repr__(self):
        if self.formatted:
            pair = self.items()
        else:
            pair = self._dict.items()
        args = ['%s=%s' % (key, repr(value)) for key, value in pair]
        arg_string = ', '.join(args)
        return '<%s(%s)>' % (self.__class__.__name__, arg_string)

    def __setattr__(self, key, value):
        if key not in self.validator.properties:
            raise AttributeError('Invalid attribute "%s"' % key)
        validator = self.validator.properties[key]
        try:
            value = validator.validate(value)
        except ValidationError as ex:
            raise ValidationError({validator.title or key: ex.detail})
        self._dict[key] = value

    def __setitem__(self, key, value):
        if key not in self.validator.properties:
            raise KeyError('Invalid key "%s"' % key)
        value = self.validator.properties[key].validate(value)
        self._dict[key] = value

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        del self._dict[key]
        if self.formatted:
            self._dict[key] = self.validator.properties[key].validate(None)

    def __getattr__(self, key):
        try:
            return self._dict[key]
        except (KeyError,):
            raise AttributeError('Invalid attribute "%s"' % key)

    def __getitem__(self, key):

        validator = self.validator.properties.get(key)
        try:
            value = self._dict[key]
        except KeyError as e:
            try:
                if validator:
                    value = validator.get_default()
                    self[key] = value
                else:
                    raise e
            except AssertionError:
                raise e

        if hasattr(validator, 'formatter') and validator.formatter:
            return validator.formatter.to_string(value)

        return value

    def __contains__(self, item):
        return item in self._dict

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __bool__(self):
        return bool(len(self))

    @classmethod
    def init(cls, **kwargs):
        for k, v in kwargs.items():
            setattr(cls, k, v)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.validator.properties:
                setattr(self, k, v)
            else:
                self._dict[k] = v

    def reformat(self, field_name, value=None, allow_coerce=False):
        if value is None:
            value = self._dict.get(field_name)
        validator = self.__class__.validator.properties[field_name]
        try:
            val = validator.validate(value, allow_coerce=allow_coerce)
        except ValidationError as ex:
            raise ValidationError({validator.title or field_name: ex.detail})
        setattr(self, field_name, val)
        return val

    def to_dict(self):
        return json.loads(json.dumps(self, cls=TypeEncoder))

    to_json = to_dict


class PersistentTypeMeta(PersistentMeta, TypeMetaclass):
    pass


class PersistentType(Type, metaclass=PersistentTypeMeta):
    """
    拥有持久化能力的Type
    """
    pass


class AsyncType(Type):
    """
    获取属性时为空时，自动load数据
    """
    def __getattr__(self, item):
        """
        实现__getattr__是为了点获取属性时变成异步操作。
        :param item:
        :return:
        """
        loop = asyncio.get_event_loop()
        val_future = loop.create_future()
        properties = super().__getattribute__("validator").properties.keys()

        if item in properties:
            # 对于item存在于properties中的属性，则通过父类去获取
            # 若能获取到，则将future置为done。否则进行异步加载
            try:
                val = super().__getattr__(item)
                val_future.set_result(val)
            except AttributeError:
                self._load(val_future, item)
        else:
            # 不item不存在于properties中，则证明找不到item且item
            # 不是字段。直接将future设置异常。
            val_future.set_exception(AttributeError(item))
        return val_future

    def _load(self, val_future, item):
        def set_val(doc_or_exc):
            try:
                self._dict.update(doc_or_exc)
                val_future.set_result(doc_or_exc[item])
            except TypeError:
                val_future.set_exception(doc_or_exc)
            except Exception as e:
                val_future.set_exception(e)

        task = add_success_callback(self.load(), set_val)
        asyncio.get_event_loop().create_task(task)

    async def load(self):
        return NotImplemented
