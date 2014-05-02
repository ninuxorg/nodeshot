"""
Fixed Github Backend for social auth
"""

from social_auth.backends.contrib.github import GithubBackend as BaseGithubBackend,\
                                                GithubAuth


class GithubBackend(BaseGithubBackend):
    """Github OAuth authentication backend"""

    def get_user_details(self, response):
        """Return user details from Github account"""
        name = response.get('name') or ''
        details = {'username': response.get('login')}

        try:
            email = self._fetch_emails(response.get('access_token'))[0]
            if isinstance(email, dict):
                email = email['email']
        except IndexError:
            details['email'] = ''
        else:
            details['email'] = email

        try:
            # GitHub doesn't separate first and last names. Let's try.
            first_name, last_name = name.split(' ', 1)
        except ValueError:
            details['first_name'] = name
        else:
            details['first_name'] = first_name
            details['last_name'] = last_name
        return details


# Backend definition
BACKENDS = {
    'github': GithubAuth,
}
