from locust import TaskSequence, seq_task, task
from stress_test.constants import admin_token


class ClubTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        competition_id = 2021
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        self.client.get("/club/{}/clubs".format(competition_id), headers=headers, name="clubs list")

    @seq_task(2)
    @task(1)
    def not_found(self):
        competition_id = 0
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.get("/club/{}/clubs".format(competition_id), headers=headers, name="not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()