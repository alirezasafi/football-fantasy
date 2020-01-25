import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from club.models import Club
from player.models import Player
from .database_decorators import database_empty_required
from config import db
from flask import current_app
from time import sleep
import random
import datetime
from .globals import football_api, available_competitions

@database_population_update_api.route('/players')
class PopulatePlayers(Resource):
    @database_empty_required(Player)
    def get(self):
        """population order : 3"""
        clubs = Club.query.all()
        if len(clubs) ==0:
            return{'message':'first populate clubs'}, 400
        done_clubs = 1
        player_ids=[]
        for club in clubs:
            url = football_api['Player'] % club.id
            headers ={}
            headers['X-Auth-Token'] =  current_app.config['SOURCE_API_SECRET_KEY']
            resp = requests.get(url=url,headers = headers)
            try:
                players = resp.json()['squad']
                for player in players:
                    if player['id'] not in player_ids:
                        player_to_insert = Player(
                            id = player['id'],
                            name = player['name'],
                            shirt_number = player['shirtNumber'],
                            position = player['position'],
                            club_id = club.id,
                            status = 'C',
                            price = 0,
                            lastUpdated = datetime.datetime.utcnow(),
                            point = 0,
                            image= "https://www.shareicon.net/data/256x256/2016/06/30/788946_people_512x512.png"
                        )
                        player_ids.append(player['id'])
                        db.session.add(player_to_insert)
                print('club %s is done. %s clubs remaining'%(done_clubs,len(clubs)-done_clubs))
                done_clubs+=1
                sleep(5)
                db.session.commit()
            except:
                return {'message':resp.json()['message']}, 400
        

        return {'message':'players are populated'}, 200