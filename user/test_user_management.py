import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from user.models import User
from config import db
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
            password="asdfdf",
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



if __name__ == "__main__":
    unittest.main()
