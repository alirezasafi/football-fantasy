import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from user.models import User
from config import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from flask import url_for

def create_sample_user():
        user = User(
            username="asdff",
            password="asdfdf",
            email="sample@gmal.com",
            is_confirmed = True,
            is_admin = True
        )
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(
            identity={
                "id" : user.id ,
                "username": user.username,
                'is_admin': user.is_admin,
                'email': user.email,
                'is_confirmed':user.is_confirmed
            }
        )
        return access_token

def create_sample_user_username_email(username, email, id):
        user = User(
            id = id,
            username=username,
            password=generate_password_hash("asdfdf"),
            email=email,
            is_confirmed = True,
            is_admin = True
        )
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(
            identity={
                "id" : user.id ,
                "username": user.username,
                'is_admin': user.is_admin,
                'email': user.email,
                'is_confirmed':user.is_confirmed
            }
        )
        return access_token



class UserManagement(AbstractTestCase):
    def test_admin_has_access(self):
        user = User(
            username='notAdmin',
            password="asdfdf",
            email="email",
            is_confirmed = True,
            is_admin = False
        )
        db.session.add(user)
        db.session.commit()
        access_token = create_access_token(
            identity={
                "id" : user.id ,
                "username": user.username,
                'is_admin': user.is_admin,
                'email': user.email,
                'is_confirmed':user.is_confirmed
            }
        )
        headers = {'authorization':'Bearer %s'%access_token}
        response = self.client.get('/user/1', headers=headers)
        self.assertTrue(response.json.get('message') == "Only admin is privilaged.")


    def test_user_view(self):
        access_token = create_sample_user()
        create_sample_user_username_email('user2','user2@gmail.com',100)
        headers = {'authorization':'Bearer %s'%access_token}
        response = self.client.get('/user/100', headers=headers)
        self.assertTrue(response.json.get('user').get('username') == "user2")

    def test_user_delete_view(self):
        access_token = create_sample_user()
        create_sample_user_username_email('user2','user2@gmail.com',100)
        headers = {'authorization':'Bearer %s'%access_token}
        response = self.client.delete('/user/100', headers=headers)
        self.assertTrue(response.json.get('message') == "User deleted.")
    def test_user_delete_wrong_user_view(self):
        access_token = create_sample_user()
        headers = {'authorization':'Bearer %s'%access_token}
        response = self.client.delete('/user/100', headers=headers)
        self.assertTrue(response.json.get('message') == "No such user found.")


class TestProfile(AbstractTestCase):
    def test_successful(self):
        user = self.creat_user()
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        successful_response = self.client.get(url_for('profile'), headers=headers)
        self.assert200(successful_response)
        self.assertTrue(successful_response.json.get('user'))
        self.assertTrue(type(successful_response.json.get('squads')) == list)

    def test_user_not_found(self):
        access_token = create_access_token(
            identity={
                "id": 12,
                "username": "asas",
                'is_admin': False,
                'email': "asas@gmail.com",
                'is_confirmed': True
            }
        )
        headers = {'Authorization': 'Bearer ' + access_token}
        user_not_found_response = self.client.get(url_for('profile'), headers=headers)
        self.assert404(user_not_found_response)
        self.assertTrue(user_not_found_response.json.get('message'))


class TestAccount(AbstractTestCase):
    def test_delete_successful(self):
        user = self.creat_user(password="1234", is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        delete_successful_response = self.client.delete(url_for('account'), headers=headers, json=dict(password='1234'))
        self.assert200(delete_successful_response)
        self.assertTrue(delete_successful_response.json.get('message'))

    def test_delete_user_not_found(self):
        access_token = create_access_token(
            identity={
                "id": 12,
                "username": "asas",
                'is_admin': False,
                'email': "asas@gmail.com",
                'is_confirmed': True
            }
        )
        headers = {'Authorization': 'Bearer ' + access_token}
        user_not_found_response = self.client.delete(url_for('account'), headers=headers, json=dict(password="1234"))
        self.assert404(user_not_found_response)
        self.assertTrue(user_not_found_response.json.get('message'))

    def test_delete_password_incorrect(self):
        user = self.creat_user(password="12345", is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        password_incorrect_response = self.client.delete(url_for('account'), headers=headers, json=dict(password='1234'))
        self.assert400(password_incorrect_response)
        self.assertTrue(password_incorrect_response.json.get('message'))

    def test_delete_password_not_send(self):
        user = self.creat_user(password="12345", is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        password_incorrect_response = self.client.delete(url_for('account'), headers=headers,
                                                         json={})
        self.assert400(password_incorrect_response)
        self.assertTrue(password_incorrect_response.json.get('message'))


if __name__ == "__main__":
    unittest.main()
