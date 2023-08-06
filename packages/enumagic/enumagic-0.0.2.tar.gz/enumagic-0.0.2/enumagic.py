"""Python enums that work like magic."""

from enum import Enum, EnumMeta
from typing import Any, Dict, Iterator, Type, TypeVar, Tuple

_VT = TypeVar('_VT')
_ET = TypeVar('_ET', bound=Type[Enum])


class IterMeta(EnumMeta):
    """Iterable enum metaclass."""
    def __iter__(cls) -> Iterator[Tuple[str, _VT]]:
        """
        Iterate over the entries of the enum.

        Yields:
            :obj:`tuple` of :obj:`str`, :obj:`object` :

            The next tuple where the first element is the
            ``name`` of the enum instance and the second
            element is the ``value`` of the enum instance.

        Examples:
            >>> it = iter(IterExample)
            >>> next(it)
            ('A', 'Alice')
        """
        return ((e.name, e.value) for e in super().__iter__())

    def __contains__(cls, item: Any) -> bool:
        """
        Check whether the enum contains a certain item

        Args:
            item (:obj:`~typing.Any`): A string or enum instance.

        Returns:
            :obj:`bool`:

            ``True`` if the enum has a member that
            matches the given item, ``False`` otherwise.

        Raises:
            :obj:`TypeError`: If the item is not a string or enum instance.

        Examples:
            >>> 'B' in IterExample
            True
            >>> 'C' in IterExample
            False
        """
        if isinstance(item, str):
            return item in cls.__members__
        return super().__contains__(item)


class MappingMeta(EnumMeta):
    """Mapping enum metaclass."""
    def __iter__(cls) -> Iterator[Tuple[int, str]]:
        """
        Iterate over the values of the enum.

        Yields:
            :obj:`tuple` of :obj:`int`, :obj:`str` :

            The next tuple where the first element is the
            ``index`` of the enum instance and the second
            element is the ``label`` of the enum instance.

        Examples:
            >>> list(MappingExample)
            [(0, 'Alice'), (1, 'Bob')]
        """
        return (e.value for e in super().__iter__())

    def __call__(cls, value: Any) -> _ET:
        """
        Get an enum instance from the given value.

        Args:
            value (:obj:`~typing.Any`):
                The value to look for in the members of the enum.

        Returns:
            :obj:`~enum.Enum`: An enum instance that corresponds to the value.

        Raises:
            :obj:`ValueError`: If the given value is invalid.

        Examples:
            >>> MappingExample(0)
            <MappingExample.A: (0, 'Alice')>
            >>> MappingExample('Bob')
            <MappingExample.B: (1, 'Bob')>
        """
        if isinstance(value, int):
            value = next((v for v in cls if v[0] == value), value)
        elif isinstance(value, str):
            value = next((v for v in cls if v[1] == value), value)
        return super().__call__(value)

    @property
    def items(cls) -> Dict[str, int]:
        """
        Get a mapping of ``label``/``index`` pairs.

        Type
            :obj:`dict` of :obj:`str` to :obj:`int`

        Examples:
            >>> MappingExample.items
            {'Alice': 0, 'Bob': 1}
        """
        return {lbl: idx for idx, lbl in cls}

    @property
    def indices(cls) -> Tuple[int, ...]:
        """
        Get the indices of the enum.

        Type
            :obj:`tuple` of :obj:`int`

        Examples:
            >>> MappingExample.indices
            (0, 1)
        """
        return tuple(val[0] for val in cls)

    @property
    def labels(cls) -> Tuple[str, ...]:
        """
        Get the labels of the enum.

        Type
            :obj:`tuple` of :obj:`str`

        Examples:
            >>> MappingExample.labels
            ('Alice', 'Bob')
        """
        return tuple(val[1] for val in cls)


class IterEnum(Enum, metaclass=IterMeta):
    """
    Enum class that can be used as an iterable.

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enumagic.IterMeta`

    Examples:
        >>> class IterExample(IterEnum):
        ...     A = 'Alice'
        ...     B = 'Bob'
        >>> dict(IterExample)
        {'A': 'Alice', 'B': 'Bob'}
    """


class MappingEnum(Enum, metaclass=MappingMeta):
    """
    Enum class which maps labels to indices.

    Attributes:
        index (int): An integer that will be used as the index.
        label (str): A string that will be used as the label.

    Examples:
        >>> class MappingExample(MappingEnum):
        ...     A = 0, 'Alice'
        ...     B = 1, 'Bob'
        >>> '%d, %s' % (MappingExample.B.index, Example.B.label)
        '1, Bob'

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enumagic.MappingMeta`

    .. automethod:: __str__() -> str
    """
    def __init__(self, index: int, label: str):
        if index in self.__class__.indices:
            raise ValueError('Duplicate index found: %d' % index)
        if label in self.__class__.labels:
            raise ValueError('Duplicate label found: %s' % label)
        self.index, self.label = index, label

    def __str__(self) -> str:
        """
        Return the instance as a string.

        Returns:
            :obj:`str`: The label of the instance.

        Examples:
            >>> str(MappingExample.A)
            'Alice'
        """
        return self.label

    def __int__(self) -> int:
        """
        Return the instance as an integer.

        Returns:
            :obj:`int`: The index of the instance.

        Examples:
            >>> int(MappingExample.A)
            0
        """
        return self.index

    def __index__(self) -> int:
        """
        Return the instance as an index.

        Returns:
            :obj:`int`: The index of the instance.

        Examples:
            >>> test = ['first', 'second']
            >>> test[MappingExample.B]
            'second'
        """
        return self.index


class StrEnum(str, Enum):
    """
    Enum class that be used as a string.

    Examples:
        >>> class StrExample(StrEnum):
        ...     A = 'Alice'
        >>> StrExample.A.upper()
        'ALICE'

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enum.EnumMeta`

    .. automethod:: __str__() -> str
    """
    def __str__(self) -> str:
        """
        Return the instance as a string.

        Returns:
            :obj:`str`: The value of the instance.

        Examples:
            >>> str(StrExample.A)
            'Alice'
        """
        return self.value


class ChoiceMeta(IterMeta):
    """Choice enum metaclass."""
    def __new__(meta, *args, **kwargs):
        cls = super().__new__(meta, *args, **kwargs)
        cls.do_not_call_in_templates = True
        return cls

    def __getitem__(cls, name: str) -> str:
        """
        Get the value of an enum member.

        Args:
            name (:obj:`str`): The name of the item.

        Returns:
            :obj:`str`: The value of the instance.

        Examples:
            >>> ColorChoice['GREEN']
            '#0F0'
        """
        return super().__getitem__(name).value


class ChoiceEnum(str, Enum, metaclass=ChoiceMeta):
    """
    Enum class that can be used as Django `field choices`_.

    Examples:
        >>> from django.db.models import CharField, Model
        >>> class ColorChoice(ChoiceEnum):
        ...     RED = '#F00'
        ...     GREEN = '#0F0'
        ...     BLUE = '#00F'
        >>> class Color(Model):
        ...     color = CharField(choices=ColorChoice)
        >>> example = Color(color=ColorChoice.RED)
        >>> example.get_color_display()
        '#F00'

    .. autoattribute:: do_not_call_in_templates
        :annotation: = True

        Prevent the Django `template system`_ from calling the enum.

    .. autoattribute:: __class__
        :annotation:

        alias of :class:`enumagic.django.ChoiceMeta`

    .. automethod:: __str__() -> str

    .. automethod:: __eq__(other: Any) -> bool

    .. _field choices:
        https://docs.djangoproject.com/en/3.0/ref
        /models/fields/#django.db.models.Field.choices

    .. _template system:
        https://docs.djangoproject.com/en/3.0/ref
        /templates/api/#variables-and-lookups
    """
    def __str__(self) -> str:
        """
        Return the instance as a string.

        Returns:
            :obj:`str`: The name of the instance.

        Examples:
            >>> str(ColorChoice.BLUE)
            'BLUE'
        """
        return self.name

    def __hash__(self) -> int:
        """
        Return the hash of the instance.

        Returns:
            :obj:`int`: The hashed name.

        Examples:
            >>> hash(ColorChoice.RED)
            364091286298964602
        """
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        """
        Check whether the objects are equal.

        Args:
            other (:obj:`~typing.Any`): Another object.

        Returns:
            :obj:`bool`:

            ``True`` if the objects are equal as strings, ``False`` otherwise.

        Examples:
            >>> ColorChoice.GREEN == 'GREEN'
            True
        """
        return str(self) == str(other)


django = __import__('types').ModuleType('django')
django.__doc__ = 'Special enums for Django.'

django.ChoiceMeta = ChoiceMeta
django.ChoiceMeta.__module__ += '.django'

django.ChoiceEnum = ChoiceEnum
django.ChoiceEnum.__module__ += '.django'

del ChoiceMeta, ChoiceEnum
