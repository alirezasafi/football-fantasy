from locust import TaskSequence, task, seq_task
from stress_test.constants import admin_token
from stress_test.team import LoginTasks


class ProfileTasks(TaskSequence):
    @seq_task(1)
    @task(1)
    def success(self):
        token = admin_token
        headers = {"Authorization": "Bearer {}".format(token)}
        self.client.get("/user/profile", headers=headers, name="profile success")

    @seq_task(2)
    @task(1)
    def delete_account_success(self):
        token = LoginTasks.tokens.get()
        LoginTasks.tokens.put(token)
        headers = {"Authorization": "Bearer {}".format(admin_token)}
        self.client.post("/user/account", headers=headers, json={"password": "1234"}, name="delete account success")

    # @seq_task(3)
    # @task(1)
    # def stop(self):
    #     self.interrupt()
