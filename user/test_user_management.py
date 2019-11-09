import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from user.models import User
from config import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
import random


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
    def test_profile_view(self):
        access_token = create_sample_user_username_email('ali','ali@gmail.com',1)
        headers = {'Authorization': 'Bearer '+ access_token}
        response = self.client.get('/user/profile', headers=headers)
        self.assertTrue(response.json.get('username') == 'ali')

    def test_profile_update_username(self):
        access_token = create_sample_user_username_email('ali','ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer '+ access_token}
        response = self.client.put('/user/profile', headers=headers, json=dict(username="new.ali",password=None, email=None))
        self.assertTrue(response.json.get('message') == 'successfully updated')

    def test_profile_update_password(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.put('/user/profile', headers=headers,
                                   json=dict(username=None, password='1234', email=None))
        self.assertTrue(response.json.get('message') == 'successfully updated')

    def test_profile_update_email(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.put('/user/profile', headers=headers,
                                   json=dict(username=None, password=None, email='new.ali@gmail.com'))
        self.assertTrue(response.json.get('message') == 'successfully updated, confirmation email is sent to your email.')

    def test_profile_update_all(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.put('/user/profile', headers=headers,
                                   json=dict(username='new.alir', password='1234', email='new.ali@gmail.com'))
        self.assertTrue(
            response.json.get('message') == 'successfully updated, confirmation email is sent to your email.')

    def test_profile_unchanged(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.put('/user/profile', headers=headers,
                                   json=dict(username=None, password=None, email=None))
        self.assertTrue(response.json.get('message') == 'there is no change')

    def test_profile_update_already_register(self):
        create_sample_user_username_email('new.ali', 'new.ali@gmail.com', 2)
        access_token1 = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token1}
        response = self.client.put('/user/profile', headers=headers,
                                   json=dict(username='new.ali', password=None, email=None))
        self.assertTrue(response.json.get('message') == 'User already registered')

    def test_delete_account(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.delete('/user/profile', headers=headers, json=dict(password='asdfdf'))
        self.assertTrue(response.json.get('message') == 'successfully deleted.')

    def test_delete_account_password_wrong(self):
        access_token = create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.delete('/user/profile', headers=headers, json=dict(password='asasasdfdf'))
        self.assertTrue(response.json.get('message') == 'password is incorrect!')


if __name__ == "__main__":
    unittest.main()
