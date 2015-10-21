__author__ = 'Jableader'

from django.contrib.auth.models import User

from rest_framework.test import force_authenticate
from rest_framework.test import APIClient, APITestCase

from api.models import *

class TestLists(APITestCase):

    def setUp(self):
        bob = User.objects.create_user('Bob', 'bob@b.com', 'bobs_password')
        bob.save()

        bill = User.objects.create_user('Bill', 'bill@b.com', 'bills_password')
        bill.save()

        self.bill, self.bob = bill, bob

    def test_create_list(self):
        self.client.force_authenticate(user=self.bob)
        response = self.client.post('/list/', data={'title': 'Test create', 'description': 'Test list'})

        self.assertEqual(response.status_code, 201)

        created_list = List.objects.get(title='Test create')
        self.assertIsNotNone(created_list)
        self.assertEqual(created_list.owner, self.bob)

    def test_cant_change_owner(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)

        self.client.patch('/list/%d' % l.pk, {'owner': self.bill.pk}, follow=True)

        l.refresh_from_db()
        self.assertEqual(self.bob, l.owner)

    def test_create_list_anonymous(self):
        response = self.client.post('/list/', data={'title': 'Test create', 'description': 'Test list'})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(List.objects.filter(title='Test create').count(), 0)

    def test_get_list(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        l.items.create(caption='First', description='Not blank')
        l.items.create(caption='Second', description='Not blank')


        response = self.client.get('/list/%d' % l.pk, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'My List')
        items = response.data['items']
        self.assertEqual(len(items), 2)

    def test_get_list_by_title(self):

        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        l.items.create(caption='First', description='Not blank')
        l.items.create(caption='Second', description='Not blank')


        response = self.client.get('/list/%s/get_list_by_title' % l.title, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_list_by_user(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        response = self.client.get('/list/%s/get_list_by_user' % l.owner.username, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)




class TestItems(APITestCase):
    def setUp(self):
        TestLists.setUp(self) # Yeah I know, its odd

    def test_add_item_to_list(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        self.client.force_authenticate(user=self.bob)

        caption = 'My Caption'
        description = 'Some Item'

        response = self.client.post('/item/', data={'caption': caption, 'description': description, 'list': l.pk})
        self.assertEqual(response.status_code, 201, msg=str(response.data))

        created_item = Item.objects.get(caption=caption)
        self.assertEqual(created_item.description, description)
        self.assertEqual(created_item.list, l)

    def test_delete_item(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        toDelete = l.items.create(caption='First', description='Not blank')
        notDeleted = l.items.create(caption='Second', description='Not blank')

        response = self.client.delete('/item/%d' %toDelete.pk, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, l.items.count())
        self.assertEqual(l.items.first(), notDeleted)

    def test_cant_modify_anothers_list(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        self.client.force_authenticate(user=self.bill)

        response = self.client.post('/item/', data={'caption': 'blah', 'description': 'blah', 'list': l.pk})

        self.assertEqual(403, response.status_code)
        self.assertEqual(0, l.items.count())

    def test_can_modify_own_list(self):
        l = List.objects.create(title='My List', description='Blah', owner=self.bob)
        self.client.force_authenticate(user=self.bob)

        response = self.client.put('/list/%d' % l.pk, {'title': 'Bobs List'}, follow=True)

        self.assertEqual(200, response.status_code)

        l.refresh_from_db()
        self.assertEqual('Bobs List', l.title)
        self.assertEqual('Blah', l.description)