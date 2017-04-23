"""
Forms for saving ShowBadge items.
"""
from django.forms import ModelForm

from .github import GitHubApi
from .models import ShowBadgeItem


class ShowBadgeItemForm(ModelForm):
    """
    Form to save a ShowBadgeItem.
    """

    class Meta:
        model = ShowBadgeItem
        fields = ('commit', 'key', 'value')

    def save(self):
        GitHubApi.check_commit(self.instance.user, self.instance.repo, self.instance.commit)
        return super().save()
