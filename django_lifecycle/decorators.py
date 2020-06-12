from functools import wraps
from typing import List

from . import NotSet, HookSpec
from .hooks import VALID_HOOKS


class DjangoLifeCycleException(Exception):
    pass


def _validate_hook_params(spec: HookSpec):
    if spec.hook_name not in VALID_HOOKS:
        raise DjangoLifeCycleException(
            "%s is not a valid hook; must be one of %s" % (hook, VALID_HOOKS)
        )

    if spec.has_changed is not None and not isinstance(spec.has_changed, bool):
        raise DjangoLifeCycleException("'has_changed' hook param must be a boolean")

    if spec.when is not None and not isinstance(spec.when, str):
        raise DjangoLifeCycleException(
            "'when' hook param must be a string matching the name of a model field"
        )

    if spec.when_any is not None:
        when_any_error_msg = (
            "'when_any' hook param must be a list of strings "
            "matching the names of model fields"
        )

        if not isinstance(spec.when_any, list):
            raise DjangoLifeCycleException(when_any_error_msg)

        if len(spec.when_any) == 0:
            raise DjangoLifeCycleException(
                "'when_any' hook param must contain at least one field name"
            )

        for field_name in spec.when_any:
            if not isinstance(field_name, str):
                raise DjangoLifeCycleException(when_any_error_msg)

    if spec.when is not None and spec.when_any is not None:
        raise DjangoLifeCycleException(
            "Can pass either 'when' or 'when_any' but not both"
        )


class HookedMethod:
    """
    Replacement for original method with stored information about registered hook.
    """

    def __init__(self, f, hook_spec: HookSpec):
        self._f = f
        self._hooked = f._hooked if isinstance(f, type(self)) else []  # type: List[HookSpec]
        # FIFO to respect order of @hook decorators definition
        self._hooked.append(hook_spec)
        self.__name__ = f.__name__

    def __get__(self, instance, owner):
        """
        Getter descriptor for access directly from class -> ModelA.<name>.
        Used in LifecycleModelMixin._potentially_hooked_methods for detection hooked methods.
        """
        if not instance:
            return self
        return self._f

    def __call__(self, *args, **kwargs):
        """
        Calling directly as model_instance.hooked_method().
        """
        return self._f(*args, **kwargs)

    @property
    def specs(self) -> List[HookSpec]:
        return self._hooked


def hook(
        hook: str,
        when: str = None,
        when_any: List[str] = None,
        was="*",
        is_now="*",
        has_changed: bool = None,
        is_not=NotSet,
        was_not=NotSet,
        changes_to=NotSet,
):
    spec = HookSpec(
        hook_name=hook,
        when=when,
        when_any=when_any,
        has_changed=has_changed,
        is_now=is_now,
        is_not=is_not,
        was=was,
        was_not=was_not,
        changes_to=changes_to
    )

    _validate_hook_params(spec)

    return lambda fnc: wraps(fnc)(HookedMethod(fnc, spec))
