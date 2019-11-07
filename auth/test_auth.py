import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from Testcase import AbstractTestCase

class TestAuthentication(AbstractTestCase):

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




if __name__ == "__main__":
    unittest.main()
