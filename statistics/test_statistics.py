from Testcase import AbstractTestCase
from flask import url_for


class TestPlayerStatistics(AbstractTestCase):
    def test_not_found(self):
        query_p = {'player_id': 10}
        not_found_response = self.client.get(url_for('player_statistic', **query_p))
        self.assertTrue(not_found_response.json.get('message'))
        self.assert404(not_found_response)

    def test_successful(self):
        player = self.create_player()
        query_p = {'player_id': player.id}
        successful_response = self.client.get(url_for('player_statistic', **query_p))
        self.assert200(successful_response)
        self.assertTrue(successful_response.json.get('player'))
        self.assertTrue(type(successful_response.json.get('events')) == list)
        self.assertTrue(successful_response.json.get('club'))
        self.assertTrue(type(successful_response.json.get('matches')) == list)


class TestSquadStatistics(AbstractTestCase):
    def test_successful(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        competition = self.create_competition()
        self.create_squad(user=user, competition=competition)
        query_p = {'competition_id': competition.id}
        headers = {'Authorization': 'Bearer ' + access_token}
        successful_response = self.client.get(url_for('squad_statistic', **query_p), headers=headers)
        self.assert200(successful_response)
        self.assertTrue(type(successful_response.json.get('squad')) == list)

    def test_squad_not_found(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        competition = self.create_competition()
        query_p = {'competition_id': competition.id}
        headers = {'Authorization': 'Bearer ' + access_token}
        squad_not_found_response = self.client.get(url_for('squad_statistic', **query_p), headers=headers)
        self.assert400(squad_not_found_response)
        self.assertTrue(squad_not_found_response.json.get('message'))

    def test_competition_not_found(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        query_p = {'competition_id': 10}
        headers = {'Authorization': 'Bearer ' + access_token}
        competition_not_found_response = self.client.get(url_for('squad_statistic', **query_p), headers=headers)
        self.assertTrue(competition_not_found_response.json.get('message'))
        self.assert404(competition_not_found_response)
