from locust import TaskSequence, seq_task, task
from stress_test.constants import admin_token


class CompetitionTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        self.client.get("/competition/list", headers=headers, name="competition list")
