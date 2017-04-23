"""
Tools for using GitHub API.
"""
import requests


class GitHubApi:
    """
    GitHub API tool.

    GitHubApi provides some information of user's GitHub repository by using
    GitHub API v3 automatically.

    For more informatioin, see `GitHub API v3`_

    .. _`GitHub API v3`: https://developer.github.com/v3/
    """

    GITHUB_API_GET_REPO = "https://api.github.com/repos/{user}/{repo}"
    GITHUB_API_GET_BRANCH = GITHUB_API_GET_REPO + "/branches/{branch}"
    GITHUB_API_GET_COMMIT = GITHUB_API_GET_REPO + "/git/commits/{sha}"

    @classmethod
    def get_branch(cls, user, repo, branch):
        """
        Returns the latest commit SHA value for the given branch.

        Raises an exception if there is no such branch.

        Args:
            user (:obj:`str`): GitHub username.
            repo (:obj:`str`): GitHub repository name of the given user.
            branch (:obj:`str`): GitHub branch name of the given repository.

        Returns:
            :obj:`str`: The latest commit SHA value for the given branch.

        Raises:
            :obj:`HTTPError`: If `user`, `repo`, or `branch` does not exist.
        """
        url = cls.GITHUB_API_GET_BRANCH.format(
            user=user, repo=repo, branch=branch)
        res = requests.get(url)
        res.raise_for_status()
        return res.json()['commit']['sha']

    @classmethod
    def check_commit(cls, user, repo, sha):
        """
        Raises an exception if the repository does not have the given commit.

        Args:
            user (:obj:`str`): GitHub username.
            repo (:obj:`str`): GitHub repository name of the given user.
            sha (:obj:`str`): SHA value of the desired commit.

        Raises:
            :obj:`HTTPError`: If commit with `sha` does not exit in `repo` of
                `user` or if `user` or `repo` is invalid.
        """
        url = cls.GITHUB_API_GET_COMMIT.format(
            user=user, repo=repo, sha=sha)
        res = requests.get(url)
        res.raise_for_status()
