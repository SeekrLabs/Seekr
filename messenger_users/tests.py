from django.test import TestCase, Client
from django.urls import reverse
from .models import MessengerUser
from postings.models import Posting
from .views import *
from django.http import HttpRequest
import json
from pprint import pprint

class MessengerUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def add_objects(self):
        posting = Posting(pk='test', title='test', url='https://google.com')
        posting.save()
        user = MessengerUser(pk='test')
        user.save()

    def test_view_posting_dne_user(self):
        response = self.client.get(reverse('view_posting') + 
            '?posting_id=test&messenger_id=test')
        assert(response.status_code == 404)

    def test_view_posting_dne_posting(self):
        user = MessengerUser(pk='test')
        user.save()
        response = self.client.get(reverse('view_posting') + 
            '?posting_id=test&messenger_id=test')
        assert(response.status_code == 404)

    def test_view_posting(self):
        self.add_objects()
        user = MessengerUser(pk='test')
        user.save()
        response = self.client.get(reverse('view_posting') + 
            '?posting_id=test&messenger_id=test')
        assert(response.status_code == 302)
        assert(response.url == 'https://google.com')

    def test_save_posting(self):
        self.add_objects()
        postings = Posting.objects.filter(messengeruser__id='test')
        assert(len(postings) == 0)

        response = self.client.post(
            '/messenger_users/save_posting',
            content_type='application/json',
            data={'messenger_id': 'test', 'posting_id': 'test'}
        )
        
        assert(json.loads(response.content)['status'] == 'success')
        postings = Posting.objects.filter(messengeruser__id='test')
        assert(len(postings) == 1)
    
    def test_delete_saved_posting(self):
        self.test_save_posting()
        response = self.client.post(
            '/messenger_users/remove_saved_posting',
            content_type='application/json',
            data={'messenger_id': 'test', 'posting_id': 'test'}
        )
        postings = Posting.objects.filter(messengeruser__id='test')
        assert(len(postings) == 0)
    
    def test_browse_saved_posting(self):
        self.test_save_posting()
        response = self.client.post(
            '/messenger_users/browse_saved_postings',
            content_type='application/json',
            data={'messenger_id': 'test', 'saved_posting_page': '0'}
        )
        data = json.loads(response.content)
        print(json.dumps(data, indent=4))
        assert(len(data['messages'][0]['attachment']['payload']['elements']) == 1)