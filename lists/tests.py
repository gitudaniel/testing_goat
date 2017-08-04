import re

from django.template.loader import render_to_string
from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List


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




class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'lists/list.html')

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)



class ListAndItemModelTest(TestCase):

    def test_saving_and_retreiving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        # The .text refers to a TextField in the model item
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)




class NewListTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
                f'/lists/{correct_list.id}/add_item',
                data={'item_text': 'A new list item for an existing list'}
        )
     
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item for an existing list')
        self.assertEqual(new_item.list, correct_list)


    def test_redirects_after_POST(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
                f'/lists/{correct_list.id}/add_item',
                data={'item_text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

