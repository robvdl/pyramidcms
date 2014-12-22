from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget
from pyramid.httpexceptions import HTTPFound

from pyramidcms.layouts.base import BaseLayout
from pyramidcms.models.auth import User


class AuthViews(BaseLayout):
    """
    Authentication views: login, logout.
    """

    @view_config(route_name='login', renderer='login.jinja2')
    @forbidden_view_config(renderer='login.jinja2')
    def login(self):
        return_url = self.request.POST.get('url', self.request.url)

        # FIXME: this could potentially be a form using WTForms
        if self.request.method == 'POST':
            username = self.request.POST.get('username')
            password = self.request.POST.get('password')
            user = User.objects.get(username=username)
            if user and user.check_password(password):
                headers = remember(self.request, username)
                # refresh csrf_token on login for some extra security
                self.session.new_csrf_token()
                self.session.flash('You are logged in', queue='success')
                return HTTPFound(location=return_url, headers=headers)
            self.session.flash('Invalid username or password', queue='error')

        return {
            'return_url': return_url,
        }

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        redirect_url = self.request.route_url('home')
        return HTTPFound(location=redirect_url, headers=headers)
