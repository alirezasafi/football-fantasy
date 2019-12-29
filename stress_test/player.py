from locust import TaskSequence, seq_task, task
from.constants import admin_token


class CompetitionPlayerTasks(TaskSequence):
    def get_req(self, token, competition, name, status_code):
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.get("/player/{}/pick-squad".format(competition), catch_response=True, headers=headers, name=name) as response:
            if response.status_code == status_code:
                response.success()

    @seq_task(1)
    @task(1)
    def not_found(self):
        token = admin_token
        self.get_req(token=token, competition="000", name="competition not found", status_code=404)

    @seq_task(2)
    @task(1)
    def success(self):
        token = admin_token
        competition = 2021
        self.get_req(token=token, competition=competition, name="players of {}".format(competition), status_code=200)

    # @seq_task(3)
    # @task(1)
    # def stop(self):
    #     self.interrupt()