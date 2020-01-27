from locust import HttpLocust, constant, TaskSequence
from stress_test import (
    RegisterTasks, LoginTasks, CompetitionPlayerTasks, PickSquadTasks, GetManageTeamTask,
    TransferTasks, PlayerStatisticsTasks, CurrentWMTasks, MatchDetailTasks, SquadStatisticsTasks,
    ClubTasks, CompetitionTasks, ProfileTasks, CardsTasks, admin_token
)


class MainTasks(TaskSequence):
    tasks = [RegisterTasks, LoginTasks, CompetitionPlayerTasks, PickSquadTasks, GetManageTeamTask,
             TransferTasks, PlayerStatisticsTasks, CurrentWMTasks, MatchDetailTasks, SquadStatisticsTasks,
             ClubTasks, CompetitionTasks, ProfileTasks, CardsTasks]

    def teardown(self):
        if admin_token != "":
            headers = {'Authorization': 'Bearer {}'.format(admin_token)}
            self.client.delete('/user/list', headers=headers, name="clean data base")


class WebsiteUser(HttpLocust):
    task_set = MainTasks
    host = "http://0.0.0.0:5000"
    wait_time = constant(1)
