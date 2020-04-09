from locust import TaskSequence, task, seq_task
from stress_test import LoginTasks, competitions
from .constants import squad_data, admin_token


class PickSquadTasks(TaskSequence):
    squad_data = []

    def post_req(self, data, competition, status_code, name):
        token = LoginTasks.tokens.get()
        LoginTasks.tokens.put(token)
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.post("/team/{}/pick-squad".format(competition), catch_response=True, json=data,
                              headers=headers, name=name) as response:
            if response.status_code == status_code:
                response.success()

    @seq_task(1)
    @task(1)
    def wrong_position(self):
        data = squad_data
        data["squad"][0]["position"] = "Midfielder"
        self.post_req(data=data, competition=2021, status_code=400, name="wrong position error")
        data["squad"][0]["position"] = "Forward"

    @seq_task(2)
    @task(1)
    def wrong_select_captain(self):
        data = squad_data
        data["squad"][10]["lineup"] = False
        self.post_req(data=data, competition=2021, status_code=400, name="wrong select captain")
        data["squad"][10]["lineup"] = True

    @seq_task(3)
    @task(1)
    def formation_error(self):
        data = squad_data
        data["squad"][9]["lineup"] = False
        self.post_req(data=data, competition=2021, status_code=400, name="formation error")
        data["squad"][9]["lineup"] = True

    @seq_task(4)
    @task(1)
    def pick_fake_squad(self):
        data = squad_data
        data["squad"][9]["name"] = "asasassa"
        self.post_req(data=data, competition=2021, status_code=400, name="fake data error")
        data["squad"][9]["name"] = "Shane Duffy"

    @seq_task(1)
    @task(1)
    def success(self):
        data = squad_data
        self.post_req(data=data, competition=2021, status_code=201, name="picks squad success")

    @seq_task(6)
    @task(1)
    def pick_again(self):
        data = squad_data
        self.post_req(data=data, competition=2021, status_code=400, name="picks again error")

    @seq_task(2)
    @task(1)
    def stop(self):
        self.interrupt()


class GetManageTeamTask(TaskSequence):
    def get_req(self, token, competition, name, status_code):
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.get("/team/{}/my-team".format(competition), catch_response=True, headers=headers, name=name) as response:
            if response.status_code == status_code:
                response.success()

    @seq_task(1)
    @task(1)
    def success(self):
        token = admin_token
        self.get_req(token=token, competition=2021, name="my team success", status_code=200)

    @seq_task(2)
    @task(1)
    def squad_not_found(self):
        token = admin_token
        self.get_req(token=token, competition=2003, name="squad not picked", status_code=400)

    @seq_task(3)
    @task(1)
    def stop(self):
        self.interrupt()


class CardsTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def get_success(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        competition = 2021
        self.client.get("/team/{}/my-team/cards".format(competition), headers=headers, name="cards get success")
