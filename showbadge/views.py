"""
Views for the ShowBadge service.
"""
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from .forms import ShowBadgeItemForm
from .github import GitHubApi
from .models import ShowBadgeItem
from .shields import Shields


class ShowBadgeView(View):
    """
    ShowBadge view.

    ShowBadgeView provides storing and retrieving ShowBadge items. If the user
    request was given by POST then it stores the given item into the database.
    For GET request, it retrieves the redirection to a shields.io badge url
    for the requested item.

    The basic URL to enter to ShowBadgeView is `/{username}/{repo}`. To store
    an item, valid `commit`, `key`, and `value` should be given in the POST
    request with this URL. If the registration failed, returns a 400 error.
    Be sure that `commit` should be the full SHA value of the commit.

    To retrieve an item, valid `branch` and `key` should be given in the GET
    parameter with above URL. If the desired item was successfully found, it
    makes the corresponding ShieldsIO badge URL and redirects to that URL.
    There would be two cases of failure in general, (1) requested parameters
    are missing or invalid, (2) user-repo-branch exists but an item for the
    newest commit for that branch has not be arrived yet, maybe due to delays
    on CI or something else. First case would return 404 error, but be sure
    that second would make a badge with `undefined` string.

    With GET request, user can set `color` parameter. This is an option, so
    this works well without `color`. To know how `color` can be determined,
    see ``ShieldsIO`` class.

    Note that CSRF protection is off for this view.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Fetch user and repo from the requested URL.
        user = kwargs['user']
        repo = kwargs['repo']

        # Save a ShowBadge item and returns the reponse.
        item = ShowBadgeItem(user=user, repo=repo)
        form = ShowBadgeItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return HttpResponse()
        raise SuspiciousOperation()

    def get(self, request, *args, **kwargs):
        # Fetch attributes to determine the requested item.
        user = kwargs['user']
        repo = kwargs['repo']
        branch = request.GET.get('branch')
        key = request.GET.get('key')
        if None in [branch, key]:
            raise Http404
        color = request.GET.get('color')

        # Find SHA of the latest commit for the given branch.
        commit = GitHubApi.get_branch(user, repo, branch)

        # Retrive the desired item.
        item = ShowBadgeItem.objects.filter(user=user, repo=repo, commit=commit, key=key).first()
        if item:
            value = item.value
        else:
            value = None

        # Redirect to the URL for an appropriate badge for the item.
        img_url = Shields.get_badge_url(key, value, color)
        return redirect(img_url)
