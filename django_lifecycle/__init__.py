from typing import NewType, Union, Any, Callable

from .django_info import IS_GTE_1_POINT_9


class NotSet(object):
    pass


from .decorators import hook
from .mixins import LifecycleModelMixin
from .hooks import *

Condition = NewType('Condition', Union[Any, Callable[[Any], bool]])

if IS_GTE_1_POINT_9:
    from .models import LifecycleModel
