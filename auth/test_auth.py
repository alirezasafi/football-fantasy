import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase
from user.test_user_management import create_sample_user_username_email

class TestAuthentication(AbstractTestCase):
    def test_login(self):
        create_sample_user_username_email('ali','ali@gmail.com',1)
        response = self.client.post('/auth/login', json=dict(username='ali', email='ali@gmail.com', password='asdfdf'))
        self.assertTrue(response.json.get('message') == 'successful login')

    def test_login_with_username_only(self):
        create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        response = self.client.post('/auth/login', json=dict(username='ali', password='asdfdf'))
        self.assertTrue(response.json.get('message') == 'successful login')

    def test_login_with_email_only(self):
        create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        response = self.client.post('/auth/login', json=dict(email='ali@gmail.com', password='asdfdf'))
        self.assertTrue(response.json.get('message') == 'successful login')

    def test_login_wrong_password(self):
        create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        response = self.client.post('/auth/login', json=dict(email='ali@gmail.com', password='asdsdfdf'))
        self.assertTrue(response.json.get('message') == 'wrong password')

    def test_login_uncompleted_field(self):
        create_sample_user_username_email('ali', 'ali@gmail.com', 1)
        response = self.client.post('/auth/login', json=dict(password='asdsdfdf'))

        self.assertTrue(response.json.get('message') == 'Missing credentials.')

        response = self.client.post('/auth/login', json=dict(username='ali'))
        self.assertTrue(response.json.get('message') == 'Missing credentials.')

    def test_not_registered_login(self):
        response = self.client.post('/auth/login', json=dict(
            username="asdff",
            password="asdfdf"
        ))
        self.assertTrue(response.json.get('message') == "No user found!")


    def test_uncomplete_fields_registeration(self):
        no_email_response = self.client.post('/auth/registeration', json=dict(
            username="asdff1",
            password1="asdfdf",
            password2="asdfdf",
        ))

        no_password1_response = self.client.post('/auth/registeration', json=dict(
            username="asdff2",
            password2="asdfdf",
            email="samp2le@gmal.com"
        ))

        no_password2_response = no_password1_response = self.client.post('/auth/registeration', json=dict(
            username="asdff3",
            password1="asdfdf",
            email="sampl3e@gmal.com"
        ))

        no_username_response = no_password1_response = self.client.post('/auth/registeration', json=dict(
            password1="asdfdf4",
            password2="asdfdf",
            email="sampeele@gmal.com"
        ))

        self.assertTrue(no_email_response.json.get('message') == "Compelete the fields")
        self.assertTrue(no_password1_response.json.get('message') == "Compelete the fields")
        self.assertTrue(no_password2_response.json.get('message') == "Compelete the fields")
        self.assertTrue(no_username_response.json.get('message') == "Compelete the fields")

    def test_register(self):
        response = self.client.post('/auth/registeration', json=dict(
            username="asdff",
            password1="asdfdf",
            password2="asdfdf",
            email="sample@gmal.com"
        ))
        self.assertTrue(response.json.get('message') == "Registration successful, confirmation email is sent to your email.")

    def test_same_password_register(self):
        response = self.client.post('/auth/registeration', json=dict(
            username="asdff",
            password1="asdfdf",
            password2="asdfdfwe",
            email="sample@gmal.com"
        ))
        self.assertTrue(response.json.get('message') == "Both password fileds must be the same")

    def test_already_register(self):
        create_sample_user_username_email('ali','ali@gmail.com',1)
        response = self.client.post('/auth/registeration', json=dict(
            username="ali",
            password1="asdfdf",
            password2="asdfdf",
            email="ali@gmal.com"
        ))
        self.assertTrue(response.json.get('message') == "User already registered")

    def test_whoAmI(self):
        access_token = create_sample_user_username_email('ali','ali@gmail.com',1)
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.client.get('/auth/whoami', headers=headers)
        self.assertTrue(response.json.get('info').get('username') == "ali")


if __name__ == "__main__":
    unittest.main()