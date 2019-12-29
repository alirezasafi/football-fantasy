from locust import TaskSequence, task, seq_task
from stress_test import LoginTasks, competitions
from .constants import transfer_data


class TransferTasks(TaskSequence):
    def post_req(self, data, competition, status_code, name):
        token = LoginTasks.tokens.get()
        LoginTasks.tokens.put(token)
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.post("/team/{}/my-team/transfer".format(competition), catch_response=True, json=data,
                              headers=headers, name=name) as response:
            if response.status_code == status_code:
                response.success()

    @seq_task(1)
    @task(1)
    def success(self):
        data = transfer_data
        self.post_req(data=data, competition=2021, status_code=200, name="transfer success")

    # @seq_task(2)
    # @task(1)
    # def stop(self):
    #     self.interrupt()
