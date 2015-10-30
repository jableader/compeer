from api.models import *

from api.votes import encrypt, decrypt

__author__ = 'Jableader'

from rest_framework.test import APITestCase

class TestVotes(APITestCase):

    def setUp(self):
        bob = User.objects.create_user('Bob', password='bobs_password')
        list = List.objects.create(title="My list", description="Kitchen tool", owner=bob)

        list.items.create(caption='Knife', description='Cut things')
        list.items.create(caption='Spoon', description='Spoon things')
        list.items.create(caption='Fork', description='Fork things')
        list.items.create(caption='Blender', description='Blend things')

        self.bob, self.list = bob, list

    def test_encrypt(self):
        data = bytes([i % 256 for i in range(1000)])
        decrypted = decrypt(encrypt(data))

        self.assertEqual(data, decrypted)


    def test_get_pair(self):
        response = self.client.get('/list/%d/get_pair' % self.list.pk, follow=True)

        self.assertEqual(200, response.status_code)
        self.assertTrue('vote_token' in response.data)
        self.assertTrue('pair' in response.data)
        self.assertEqual(2, len(response.data['pair']))

    def test_vote_pair(self):
        token, pair = self.get_pair()
        winner, loser = pair

        vote_data = {'vote_token': token, 'winner': winner.pk, 'loser': loser.pk}

        response = self.client.post('/list/%d/vote/' % self.list.pk, data=vote_data)

        self.assertEqual(200, response.status_code, msg=str(response.data))

        winner.refresh_from_db()
        loser.refresh_from_db()

        self.assertEqual(1, winner.score)
        self.assertEqual(0, loser.score)

    def get_pair(self):
        response = self.client.get('/list/%d/get_pair' % self.list.pk, follow=True)
        pair = (Item.objects.get(pk=item['id']) for item in response.data['pair'])
        return response.data['vote_token'], tuple(pair)

    def test_bad_token(self):
        token, pair = self.get_pair()
        winner = None
        for item in self.list.items.all():
            if item not in pair:
                winner = item
                break

        response = self.client.post('/list/%d/vote/' % self.list.pk, data={'vote_token': token, 'winner': winner.pk, 'loser': pair[0].pk})
        self.assertEqual(400, response.status_code)

        winner.refresh_from_db()
        self.assertEqual(0, winner.score)

    def test_old_token(self):
        token, pair = self.get_pair()
        winner, loser = pair

        import time
        time.sleep(45)

        vote_data = {'vote_token': token, 'winner': winner.pk, 'loser': loser.pk}

        response = self.client.post('/list/%d/vote/' % self.list.pk, data=vote_data)

        self.assertEqual(400, response.status_code, msg=str(response.data))

        winner.refresh_from_db()
        loser.refresh_from_db()

        self.assertEqual(0, winner.score)
        self.assertEqual(0, loser.score)