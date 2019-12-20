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
