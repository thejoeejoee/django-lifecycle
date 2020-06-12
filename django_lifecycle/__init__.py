from distutils.version import StrictVersion
from typing import NamedTuple, Optional, List, Type, Union, Any

import django

IS_DJANGO_GTE_1_POINT_9 = StrictVersion(django.__version__) >= StrictVersion("1.9")


class NotSet(object):
    pass


# replace call-declaration by class-declaration after drop support for python 3.5
HookSpec = NamedTuple(
    'HookSpec',
    (
        ('hook_name', str),
        ('when', Optional[str]),

        ('when_any', Optional[List[str]]),
        ('was', str),
        ('is_now', str),
        ('has_changed', Optional[bool]),

        ('is_not', Union[Type[NotSet], Any]),
        ('was_not', Union[Type[NotSet], Any]),
        ('changes_to', Union[Type[NotSet], Any]),
    ),
)
HookSpec.__new__.__defaults__ = (None, '*', '*', None, NotSet, NotSet, NotSet)

from .decorators import hook
from .mixins import LifecycleModelMixin
from .hooks import *

if IS_DJANGO_GTE_1_POINT_9:
    from .models import LifecycleModel
