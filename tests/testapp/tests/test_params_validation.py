from django.test import TestCase

from django_lifecycle import AFTER_SAVE
from django_lifecycle.decorators import DjangoLifeCycleException, _validate_hook_params


class ValidationTests(TestCase):
    def test_unknown_hook(self):
        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params('after_persist', 'id', ('id',), True)

    def test_non_boolean_has_changed(self):
        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, 'id', None, 'yes')

    def test_non_string_when(self):
        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, 42, None, True)

    def test_list_when_any(self):
        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, None, dict(), True)

        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, None, [], True)

        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, None, ['id', 42], True)

        _validate_hook_params(AFTER_SAVE, None, ('id',), True)

    def test_both_conditions(self):
        with self.assertRaises(DjangoLifeCycleException):
            _validate_hook_params(AFTER_SAVE, 'id', ('id', ), True)
