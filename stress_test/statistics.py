from locust import TaskSequence, seq_task, task
from stress_test import admin_token


class PlayerStatisticsTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        self.client.get("/statistics/player/6555", name="player statistics")

    @seq_task(2)
    @task(1)
    def not_found(self):
        with self.client.get("/statistics/player/0", name="not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    # @seq_task(3)
    # @task(1)
    # def stop(self):
    #     self.interrupt()


class SquadStatisticsTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def competition_not_found(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.get("/statistics/squad/0", headers=headers, name="competition not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @seq_task(2)
    @task(1)
    def squad_not_found(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        with self.client.get("/statistics/squad/2003", headers=headers, name="squad not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    @seq_task(3)
    @task(1)
    def success(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        self.client.get("/statistics/squad/2021", headers=headers, name="squad statistics success")

    # @seq_task(2)
    # @task(1)
    # def stop(self):
    #     self.interrupt()