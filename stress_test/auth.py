from locust import TaskSequence, seq_task, task
from random_username.generate import generate_username
from .constants import admin_token, Queue_size, admin_username
import json
from queue import Queue


class RegisterTasks(TaskSequence):
    user_registered = []

    def post_req(self, data, status_code, name):
        with self.client.post('/auth/registeration', json=data, name=name, catch_response=True) as response:
            if response.status_code == status_code:
                response.success()

    def generate_user(self):
        username = generate_username(1)[0]
        email = username + "@asas.com"
        password = "1234"
        user = {"username": username, "email": email, "password1": password, "password2": password}
        return user

    @seq_task(1)
    @task(1)
    def uncompleted_fields(self):
        data = self.generate_user()
        data['username'] = None
        self.post_req(data=data, status_code=400, name="register fields error.")

    @seq_task(2)
    @task(1)
    def already_exist(self):
        data = self.generate_user()
        data['username'] = 'alireza'
        self.post_req(data=data, status_code=403, name="register user exists.")

    @seq_task(3)
    @task(1)
    def passwords_not_match(self):
        data = self.generate_user()
        data['password2'] = "12121212"
        self.post_req(data=data, status_code=400, name="register passwords error.")

    @seq_task(4)
    @task(1)
    def success(self):
        data = self.generate_user()
        self.user_registered.append(data['username'])
        self.client.post('/auth/registeration', json=data, name="register success")

    @seq_task(5)
    @task(1)
    def active_accounts(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        self.client.get('/user/active', headers=headers, name="active")

    @seq_task(6)
    @task(1)
    def stop(self):
        self.interrupt()


class LoginTasks(TaskSequence):
    tokens = Queue(maxsize=Queue_size)

    def post_req(self, data, status_code, name):
        with self.client.post('/auth/login', json=data, name=name, catch_response=True) as response:
            if response.status_code == status_code:
                response.success()

    @seq_task(1)
    @task(1)
    def missing_cre(self):
        data = {"username": None, "password": None}
        self.post_req(data=data, status_code=400, name="login missing credentials.")

    @seq_task(2)
    @task(1)
    def not_found(self):
        data = {"username": "1212", "password": "1212"}
        self.post_req(data=data, status_code=404, name="login user not found.")

    @seq_task(3)
    @task(1)
    def wrong_password(self):
        data = {"username": admin_username, "password": "1121212"}
        self.post_req(data=data, status_code=400, name="login wrong password.")

    @seq_task(4)
    @task(1)
    def success(self):
        if self.tokens.full():
            self.tokens.queue.clear()
        data = {"username": RegisterTasks.user_registered.pop(), "password": "1234"}
        response = self.client.post("/auth/login", json=data, name="login success.")
        self.tokens.put(json.loads(response.content).get("access_token"))

    @seq_task(5)
    @task(1)
    def stop(self):
        self.interrupt()
