import re

from django.template.loader import render_to_string
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest

from lists.views import home_page

class HomePageTest(TestCase):

    def test_root_url_resolvers_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def remove_csrf(self, html_code):
        """render_to_string ignores csrf_token in template
        Django's render_to_string ignores the csrf_token in the template
        To resolve this we pass the request as an argument in expected_html
        A new csrf request is generated with every request.
        We therefore have 2 different csrf middleware tokens generated
        To take care of this we need to remove the token
        We define a function remove_csrf that substitutes the line of text
        containing the csrf middleware token with an empty string.

        Refer to:https://stackoverflow.com/questions/34629261/django-render-to-string-ignores-csrf-token
        """

        csrf_regex = r'<input[^>]+csrfmiddlewaretoken[^>]+>'
        return re.sub(csrf_regex, '', html_code)

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)
        expected_html = render_to_string('lists/home.html', request=request)
        view_html = response.content.decode()
        self.assertEqual(
                self.remove_csrf(view_html), 
                self.remove_csrf(expected_html)
        )

    def test_home_page_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['item_text'] = 'A new list item'

        response = home_page(request)

        self.assertIn('A new list item', response.content.decode())
        expected_html = render_to_string('lists/home.html',
                {'new_item_text': 'A new list item'},
                request=request)
        view_html = response.content.decode()
        self.assertEqual(
                self.remove_csrf(view_html),
                self.remove_csrf(expected_html)
        )

