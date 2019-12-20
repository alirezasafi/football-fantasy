import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from config import db
from player.models import Player
from club.models import Club
from Testcase import AbstractTestCase
from flask import url_for
from compeition.models import Competition
from player.player_marshmallow import PlayerSchema, PlayerPosition
import random

clubs = ['arsenal', 'chelsea', 'bournemouth', 'brighton', 'everton', 'liverpool', 'city', 'butnley']


def create_sample_competition():
    competition = Competition(
        name='premier',
        id='2021'
    )
    db.session.add(competition)
    db.session.commit()


def create_sample_clubs():
    premier = Competition.query.filter_by(name='premier').first()
    for i in range(len(clubs)):
        club = Club(name=clubs[i], id=i)
        premier.clubs.append(club)
        db.session.add(club)
    db.session.add(premier)
    db.session.commit()

def create_sample_players():
    for i in range(len(clubs)):
        gk, df, mf, fw = 0, 0, 0, 0
        for j in range(1, 21):
            if gk != 3:
                gk_player = Player(
                    name='%s %s' % (clubs[i], j),
                    position='Goalkeeper',
                    status='C',
                    price=random.randint(4, 7),
                    club_id=i
                )
                db.session.add(gk_player)
                gk += 1
            elif df != 6:
                df_player = Player(
                    name='%s %s' % (clubs[i], j),
                    position='Defender',
                    status='C',
                    price=random.randint(4, 7),
                    club_id=i
                )
                db.session.add(df_player)
                df += 1
            elif mf != 6:
                mf_player = Player(
                    name='%s %s' % (clubs[i], j),
                    position='Midfielder',
                    status='C',
                    price=random.randint(4, 7),
                    club_id=i
                )
                db.session.add(mf_player)
                mf += 1
            elif fw != 5:
                fw_player = Player(
                    name='%s %s' % (clubs[i], j),
                    position='Attacker',
                    status='C',
                    price=random.randint(4, 7),
                    club_id=i
                )
                db.session.add(fw_player)
                fw += 1
    db.session.commit()


class TestPickSquad(AbstractTestCase):
    def test_competition_not_found(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        query_p = {'competition_id': 10}
        headers = {'Authorization': 'Bearer ' + access_token}
        competition_not_found_response = self.client.post(url_for('pick-squad', **query_p), headers=headers)
        self.assertTrue(competition_not_found_response.json.get('message'))
        self.assert404(competition_not_found_response)

    def test_pick_wrong_position(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8]['lineup'] = False
        squad_data[0]['position'] = PlayerPosition.Attacker.name
        data = {'squad':squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        wrong_position_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assertTrue(wrong_position_response.json.get('message') == "select a squad with 15 players, consisting "
                                                                       "of: 2 Goalkeepers, 5 Defenders, "
                                                                       "5 Midfielders, 3 Forwards")
        self.assert400(wrong_position_response)

    def test_wrong_select_captain(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8]['lineup'] = False
        squad_data[0]['position'] = PlayerPosition.Attacker.name
        data = {'squad': squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        wrong_position_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assertTrue(wrong_position_response.json.get('message') == "select a squad with 15 players, consisting "
                                                                       "of: 2 Goalkeepers, 5 Defenders, "
                                                                       "5 Midfielders, 3 Forwards")
        self.assert400(wrong_position_response)

    def test_pick_wrong_formation(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        data = {'squad': squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        wrong_formation_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        print(wrong_formation_response.json)
        self.assert400(wrong_formation_response)
        self.assertTrue(wrong_formation_response.json.get('message') == "select your lineup players providing that 1 "
                                                                        "goalkeeper, at least 3 defenders and at "
                                                                        "least 1 forward. ")

    def test_pick_unreal_player(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8] = {'id': 200, "name": "asasasasas", "position": PlayerPosition.Midfielder.name, "lineup": False}
        data = {'squad':squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        unreal_player_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        print(unreal_player_response.json)
        self.assertTrue(unreal_player_response.json.get('message') == "Your selected players do not exist!!")
        self.assert400(unreal_player_response)

    def test_pick_more_than_3_player(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition, to_error=True)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8]['lineup'] = False
        data = {'squad':squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        more_than_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assertTrue(more_than_response.json.get('message') == "You can select up to 3 players from a single club!!")
        self.assert400(more_than_response)

    def test_budget_error(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8]['lineup'] = False
        data = {'squad': squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 1212}
        query_p = {'competition_id': competition.id}
        budget_error_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assertTrue(budget_error_response.json.get('message') == "Your budget is not enough!!")
        self.assert400(budget_error_response)

    def test_successful(self):
        user = self.creat_user(is_confirmed=True)
        access_token = self.create_user_access_token(user=user)
        headers = {'Authorization': 'Bearer ' + access_token}
        competition = self.create_competition()
        self.create_players_of_competition(competition=competition)
        squad = self.pick_squad_data(competition)
        player_schema = PlayerSchema(many=True, only={'name', 'id', 'position'})
        squad_data = player_schema.dump_players(squad, True)
        squad_data[0]['lineup'], squad_data[2]['lineup'], squad_data[7]['lineup'] = False, False, False
        squad_data[8]['lineup'] = False
        data = {'squad':squad_data, "name": "asasas", "captain": squad_data[1]['id'], "budget": 12}
        query_p = {'competition_id': competition.id}
        successful_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assertStatus(successful_response, 201)
        self.assertTrue(successful_response.json.get('detail'))

        # test pick again squad
        pick_again_response = self.client.post(url_for('pick-squad', **query_p), headers=headers, json=data)
        self.assert400(pick_again_response)
        self.assertTrue(pick_again_response.json.get('message') == "your team is complete!!")


if  __name__ == '__main__':
    unittest.main()