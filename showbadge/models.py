"""
Models for saving ShowBadge items.
"""
from django.db import models


class ShowBadgeItem(models.Model):
    """
    ShowBadge item model.

    ShowBadgeItem represents ShowBadge item. In this app ShowBadge item means
    an individual record for each commit with key-value information. Note that
    a single commit may deliver more than one key-values pair in some cases,
    even if they have a same key. Usually just a single key-value pair is
    anticipated to be stored for each single commit.

    ShowBadgeItem stores a datetime so users can fetch the last key-value for
    a given commit as well.

    Attributes:
        user (:obj:`CharField`): GitHub username.
        repo (:obj:`CharField`): GitHub repository name of the given user.
        commit (:obj:`CharField`): GitHub commit SHA value of the given repository.
        key (:obj:`CharField`): Key for a value to be registered for the current commit.
        value (:obj:`CharField`): Value to be stored with the given key for the current commit.
        datetime (:obj:`DateTimeField`): Datetime of the registration.
    """

    user = models.CharField(max_length=39)
    repo = models.CharField(max_length=100)
    commit = models.CharField(max_length=40)
    key = models.CharField(max_length=16)
    value = models.CharField(max_length=16)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-datetime']

    def __str__(self):
        return "{user}/{repo}/{commit} - {key} : {value}".format(
            user=self.user, repo=self.repo, commit=self.commit[:8], key=self.key, value=self.value)
