from locust import TaskSequence, seq_task, task


class CurrentWMTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        self.client.get("/match/2021/current-week-matches", name="success")

    @seq_task(1)
    @task(1)
    def not_found(self):
        with self.client.get("/match/2021/current-week-matches", name="not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    # @seq_task(3)
    # @task(1)
    # def stop(self):
    #     self.interrupt()


class MatchDetailTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        match_id = 271412
        self.client.get("/match/{}/details".format(match_id), name="success")

    @seq_task(2)
    @task(1)
    def not_found(self):
        match_id = 0
        with self.client.get("/match/{}/details".format(match_id), name="not found", catch_response=True) as response:
            if response.status_code == 404:
                response.success()

    # @seq_task(3)
    # @task(1)
    # def stop(self):
    #     self.interrupt()