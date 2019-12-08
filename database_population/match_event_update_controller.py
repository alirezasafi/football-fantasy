import requests
from flask_restplus import Resource
from .api_model import database_population_update_api
from config import db
from flask import current_app
from match.models import Match
from game_event.models import Event
from player.models import Player
import datetime
from .globals import football_api, available_competitions
from .match_event_population_controller import PopulateMatchesEvents


@database_population_update_api.route('/match-event-update')
class UpdateMatchEvents(Resource):
    def need_update(self, match, to_update):
        databaseLastUpdated = to_update.lastUpdated
        matchLastUpdated = match['lastUpdated']
        form = '%Y-%m-%dT%H:%M:%SZ'
        matchLastUpdated = datetime.datetime.strptime(matchLastUpdated, form)
        needsUpdate = matchLastUpdated > databaseLastUpdated
        return needsUpdate

    def update_match_event(self, to_update, match):
        # first update the match
        to_update.utcDate = match['utcDate']
        to_update.status = match['status']
        to_update.homeTeamScore = match.get('score').get(
            'fullTime').get('homeTeam')
        to_update.awayTeamScore = match.get('score').get(
            'fullTime').get('awayTeam')
        to_update.lastUpdated=match['lastUpdated']

        # get all match events
        events = PopulateMatchesEvents.get_match_events(match)
        # get all events from database
        dbEvents = Event.query.filter(
            Match.id == match['id']).all()
        # delete all pervious events
        for event in dbEvents:
            db.session.delete(event)
        # add all new events
        for event in events:
            db.session.add(event)
        db.session.commit()

    def get(self):
        "Update matches and events"
        all_matches = Match.query
        all_players_id = [player.id for player in Player.query.all()]
        for competition in available_competitions:
            url = football_api["MatchEvent"] % competition
            headers = {}
            headers['X-Auth-Token'] = current_app.config['SOURCE_API_SECRET_KEY']
            resp = requests.get(url, headers=headers)
            matches = resp.json()['data']
            for match in matches:
                # if the match is in the database already
                to_update = all_matches.filter(Match.id == match['id']).first()
                if to_update:
                    # if it does not need update keep going
                    if self.need_update(match, to_update) == False:
                        continue
                    # if the match needs update
                    else:
                        self.update_match_event(to_update, match)
                        continue
                else:
                    # insert match players and events
                    if len(match['homeTeam']['lineup']) == 0:
                        continue
                    if match['homeTeam']['captain']['id'] not in all_players_id or match['awayTeam']['captain']['id'] not in all_players_id or match['status'] == 'POSTPONED':
                        continue
                    PopulateMatchesEvents.insert_match_event(match)
            print("%d is done from %d competitions"%(available_competitions.index(competition)+1, len(available_competitions)))
        
        return {"message":"All matches and events are updated"}
