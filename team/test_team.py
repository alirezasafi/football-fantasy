import unittest, os, sys
currentdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from Testcase import AbstractTestCase
from auth.emailToken import generate_confirmation_token
from user.test_user_management import create_sample_user_username_email
from compeition.models import Competition, club_competition
from club.models import Club
from player.models import Player
from config import db
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


def player_serializer(player, lineup):
    if player.position.value == 'Attacker':
        return {'id': player.id, 'name': player.name, 'position': 'Forward', 'lineup': lineup}
    return {'id': player.id, 'name': player.name, 'position': player.position.value, 'lineup': lineup}


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


class TestTeam(AbstractTestCase):
    def test_pickSquad_manageTeam_transfer(self):
        access_token = create_sample_user_username_email('alireza', 'ali02reza78@gmail.com', 1)
        create_sample_competition()
        create_sample_clubs()
        create_sample_players()
        headers = {'Authorization': 'Bearer ' + access_token}
        players = Player.query
        # test pick squad with wrong position player

        squad = players.all()[0:16]
        budget = 0
        for i in range(len(squad)):
            budget += squad[i].price
            squad[i] = player_serializer(squad[i], True)

        wrong_position_player_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(wrong_position_player_response.json.get('message') == 'select a squad with 15 players, '
                                                                              'consisting of: 2 Goalkeepers, '
                                                                              '5 Defenders, 5 Midfielders, 3 Forwards')

        squad_gk = players.filter_by(position='Goalkeeper', club_id=0).all()[0:2]
        squad_df1 = players.filter_by(position='Defender', club_id=1).all()[0:3]
        squad_df2 = players.filter_by(position='Defender', club_id=2).all()[0:2]
        squad_mf1 = players.filter_by(position='Midfielder', club_id=3).all()[0:3]
        squad_mf2 = players.filter_by(position='Midfielder', club_id=4).all()[0:2]
        squad_fw = players.filter_by(position='Attacker', club_id=5).all()[0:3]

        squad = squad_gk + squad_df1 + squad_df2 + squad_mf1 + squad_mf2 + squad_fw
        players_obj = squad_gk + squad_df1 + squad_df2 + squad_mf1 + squad_mf2 + squad_fw
        budget = 0
        for i in range(len(squad)):
            budget += squad[i].price
            squad[i] = player_serializer(squad[i], True)
        # test formation error

        squad[13]['lineup'], squad[2]['lineup'], squad[7]['lineup'], squad[12]['lineup'] = False, False, False, False
        wrong_formation_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[0]['id'],
            'squad': squad
        })

        self.assertTrue(wrong_formation_response.json.get('message') == 'select your lineup players providing that 1 '
                                                                        'goalkeeper, at least 3 defenders and at '
                                                                        'least 1 forward. ')
        squad[13]['lineup'] = True
        # test wrong select captain

        squad[0]['lineup'], squad[2]['lineup'], squad[7]['lineup'], squad[12]['lineup'] = False, False, False, False
        wrong_select_captain_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[0]['id'],
            'squad': squad
        })
        self.assertTrue(
            wrong_select_captain_response.json.get('message') == 'Your selected captain must be in lineup!!')

        # test select unreal player
        temp_player = squad[0]
        squad[0] = {'id': 500, 'name': 'asasas', 'position': 'Goalkeeper', 'lineup': False}
        pick_unreal_player_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(pick_unreal_player_response.json.get('message') == 'Your selected players do not exist!!')
        squad[0] = temp_player

        # test select Repetitious player
        temp_player = squad[0]
        squad[0] = {'id': squad[1]['id'], 'name': squad[1]['name'], 'position': squad[1]['position'], 'lineup': False}
        pick_repetitious_player_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[-1]['id'],
            'squad': squad
        })
        self.assertTrue(pick_repetitious_player_response.json.get('message') == 'Your selected players do not exist!!')
        squad[0] = temp_player

        # select more than 3 players from one club
        player_club5 = player_serializer(players.filter_by(position='Midfielder', club_id=5).first(), True)
        temp_player = squad[-4]
        squad[-4] = player_club5
        more_than_three_player_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(more_than_three_player_response.json.get('message') == 'You can select up to 3 players from a '
                                                                               'single club!!')
        squad[-4] = temp_player
        # test budget
        for player in players_obj:
            player.price = 10
        db.session.commit()
        budget_not_enough_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(budget_not_enough_response.json.get('message') == 'Your budget is not enough!!')
        for player in players_obj:
            player.price = 5
        db.session.commit()

        # test successful pick squad
        successful_pick_squad_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(successful_pick_squad_response.json.get('detail') == 'your team was successfully registered')

        # test pick when squad complete
        pick_again_squad_response = self.client.post('/team/2021/pick-squad', headers=headers, json={
            'name': 'arsenal',
            'budget': budget,
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(pick_again_squad_response.json.get('message') == 'your team is complete!!')

        # # Manage team test
        # test get squad
        manage_team_get_response = self.client.get('/team/2021/my-team', headers=headers)
        self.assertTrue(len(manage_team_get_response.json.get('squad')) == 15)

        # not pick get squad
        new_access_token = create_sample_user_username_email('alireza2', 'ali02reza782@gmail.com', 2)
        new_headers = {'Authorization': 'Bearer ' + new_access_token}
        not_pick_get_response = self.client.get('/team/2021/my-team', headers=new_headers)
        self.assertTrue(not_pick_get_response.json.get('message') == 'first pick your team')

        # test successfully upgrade squad
        # test substitution and change captain
        squad[-1]['lineup'] = False
        squad[-3]['lineup'] = True
        squad_substitution_response = self.client.put('/team/2021/my-team', headers=headers, json={
            'captain': squad[-3]['id'],
            'squad': squad
        })
        self.assertTrue(squad_substitution_response.json.get('detail') == 'successfully upgraded')

        # send wrong player
        temp_player = squad[0]
        squad[0] = player_serializer(players.filter_by(position='Goalkeeper',club_id=6).first(),False)
        squad_substitution_response = self.client.put('/team/2021/my-team', headers=headers, json={
            'captain': squad[1]['id'],
            'squad': squad
        })
        self.assertTrue(squad_substitution_response.json.get('message') == 'BAD REQUEST')
        squad[0] = temp_player

        # test transfer
        # test not pick transfer
        player_in = player_serializer(players.filter_by(position='Attacker', club_id=6).first(), True)
        player_out = squad[-1]
        not_pick_transfer_response = self.client.post('/team/2021/my-team/transfer', headers=new_headers,json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(not_pick_transfer_response.json.get('message') == 'first pick your team')

        # test send unreal player
        player_in = {'id': 500, 'name': 'asasas', 'position': 'Goalkeeper', 'lineup': False}
        player_out = squad[0]
        unreal_player_transfer_response = self.client.post('/team/2021/my-team/transfer', headers=headers, json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(unreal_player_transfer_response.json.get('message') == 'BAD REQUEST')

        # test different position transfer
        player_in = player_serializer(players.filter_by(position='Attacker', club_id=6).first(), True)
        player_out = squad[1]
        different_position_transfer_response = self.client.post('/team/2021/my-team/transfer', headers=headers, json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(different_position_transfer_response.json.get('message') == 'You cannot transfer players with different position!!')

        # test transfer with own players error
        player_in = squad[-2]
        player_out = squad[-1]
        transfer_with_own_response = self.client.post('/team/2021/my-team/transfer', headers=headers, json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(transfer_with_own_response.json.get('message') == 'this player is in your team.')

        # test transfer when player_out not in squad
        player_in = player_serializer(players.filter_by(position='Attacker', club_id=6).first(), True)
        player_out = player_serializer(players.filter_by(position='Attacker', club_id=6).first(), True)
        player_out_not_inSquad_response = self.client.post('/team/2021/my-team/transfer', headers=headers, json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(player_out_not_inSquad_response.json.get('message') == 'BAD REQUEST')

        # test transfer when budget not enough
        player_in_obj = players.filter_by(position='Attacker', club_id=6).first()
        temp_price = player_in_obj.price
        player_in_obj.price = 100
        db.session.commit()
        player_in = player_serializer(player_in_obj, True)
        player_out = squad[-1]
        transfer_budget_not_enough_response = self.client.post('/team/2021/my-team/transfer', headers=headers, json={
            'player_in': player_in,
            'player_out': player_out
        })
        self.assertTrue(transfer_budget_not_enough_response.json.get('message') == 'your budget is not enough')
        player_in_obj.price = temp_price
        db.session.commit()


if  __name__ == '__main__':
    unittest.main()