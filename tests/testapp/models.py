import uuid
from datetime import datetime

import urlman
from django.core import mail
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from django_lifecycle import hook
from django_lifecycle.models import LifecycleModel


class CannotDeleteActiveTrial(Exception):
    pass


class CannotDeleteBoomer(Exception):
    pass


class CannotRename(Exception):
    pass


class Organization(LifecycleModel):
    name = models.CharField(max_length=100)


class UserAccount(LifecycleModel):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    email = models.EmailField(null=True)
    password_updated_at = models.DateTimeField(null=True)
    joined_at = models.DateTimeField(null=True)
    has_trial = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization, null=True, on_delete=models.SET_NULL)

    status = models.CharField(
        default="active",
        max_length=30,
        choices=(("active", "Active"), ("banned", "Banned"), ("inactive", "Inactive"), ("disabled", "Disabled")),
    )

    class urls(urlman.Urls):
        view = "/books/{self.pk}/"

    @hook("before_save", when="email", is_not=None)
    def lowercase_email(self):
        self.email = self.email.lower()

    @hook("before_create")
    def timestamp_joined_at(self):
        self.joined_at = timezone.now()

    @hook("after_create")
    def do_after_create_jobs(self):
        ## queue background job to process thumbnail image...
        mail.send_mail(
            "Welcome!", "Thank you for joining.", "from@example.com", ["to@example.com"]
        )

    @hook("before_update", when="password", has_changed=True)
    def timestamp_password_change(self):
        self.password_updated_at = timezone.now()

    @hook("before_delete", when="has_trial", was="*", is_now=True)
    def ensure_trial_not_active(self):
        raise CannotDeleteActiveTrial("Cannot delete trial user!")

    @hook("before_update", when="last_name", changes_to="Flanders")
    def ensure_last_name_is_not_changed_to_flanders(self):
        raise CannotRename("Oh, not Flanders. Anybody but Flanders.")

    @hook("after_update", when="organization.name", has_changed=True)
    def notify_org_name_change(self):
        mail.send_mail(
            "The name of your organization has changed!",
            "You organization is now named %s" % self.organization.name,
            "from@example.com",
            ["to@example.com"],
        )

    @hook(
        "after_update",
        when="organization.name",
        was="Hogwarts",
        is_now="Hogwarts Online",
    )
    def notify_user_they_were_moved_to_online_school(self):
        mail.send_mail(
            "You were moved to our online school!",
            "You organization is now named %s" % self.organization.name,
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_delete")
    def email_deleted_user(self):
        mail.send_mail(
            "We have deleted your account",
            "Thank you for your time.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="status", was="active", is_now="banned")
    def email_banned_user(self):
        mail.send_mail(
            "You have been banned",
            "You may or may not deserve it.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when_any=["first_name", "last_name"], has_changed=True)
    def email_user_about_name_change(self):
        mail.send_mail(
            "Update",
            "You changed your first name or your last name",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="status", was="active", is_now=lambda v: v in ('banned', 'disabled'))
    def email_deactivated_user(self):
        mail.send_mail(
            "You can not log in",
            "From now you can not log in.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="status", was=lambda v: v in ('banned', 'disabled'), is_now='active')
    def email_activated_user(self):
        mail.send_mail(
            "You can log in",
            "From now you can log in.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_save", when="password", is_now=lambda v: len(v) > 10)
    def email_user_long_password(self):
        mail.send_mail(
            "Congratulations for long password",
            "You have really long password now!",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="password", was=lambda v: len(v) > 5, is_now=lambda v: len(v) < 3)
    def email_user_got_worse_password(self):
        mail.send_mail(
            "Bad, very bad change of your password you made",
            "Bad, very bad",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("before_delete", when="joined_at", is_now=lambda v: v < datetime(1989, 12, 17))
    def restrict_delete_boomer_account(self):
        raise CannotDeleteBoomer

    @hook("after_delete", when="joined_at", is_not=lambda v: v > datetime(2015, 1, 1))
    def email_about_young_account_deletion(self):
        mail.send_mail(
            "Young account deleted",
            "Sorry, but that was really young account.",
            "from@example.com",
            ["to@example.com"],
        )

    @hook("after_update", when="username", is_now=lambda u: u == 'elon.musk')
    def email_congratulation_to_elon(self):
        mail.send_mail(
            "Welcome, Elon!",
            "Welcome to the test cases!",
            "from@example.com",
            ["to@example.com"],
        )

    @cached_property
    def full_name(self):
        return self.first_name + " " + self.last_name


class Locale(models.Model):
    code = models.CharField(max_length=20)

    users = models.ManyToManyField(UserAccount)


class ModelCustomPK(LifecycleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(null=True)
    answer = models.IntegerField(null=True, default=None)

    @hook("before_create")
    def timestamp_created_at(self):
        self.created_at = timezone.now()

    @hook("after_create")
    def answer_to_the_ultimate_question_of_life(self):
        self.answer = 42
