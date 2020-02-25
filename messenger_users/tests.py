from django.test import TestCase, Client
from .models import MessengerUser
from postings.models import Posting
from .views import *
from django.http import HttpRequest
import json
from pprint import pprint

class MessengerUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_save_posting(self):
        posting = Posting(pk='test', title='test')
        posting.save()
        user = MessengerUser(pk='test')
        user.save()
        
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
        assert(len(data['messages'][0]['attachment']['payload']['elements']) == 1)



