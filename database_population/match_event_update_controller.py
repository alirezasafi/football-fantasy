import requests
from config import db
from flask import current_app
from match.models import Match
from game_event.models import Event, MatchSubstitution
from player.models import Player
import datetime
from .globals import football_api, available_competitions
from .match_event_population_controller import PopulateMatchesEvents


def need_update(match, to_update):
    databaseLastUpdated = to_update.lastUpdated
    matchLastUpdated = match['lastUpdated']
    form = '%Y-%m-%dT%H:%M:%SZ'
    matchLastUpdated = datetime.datetime.strptime(matchLastUpdated, form)
    needsUpdate = matchLastUpdated > databaseLastUpdated
    return needsUpdate

def update_match_event(to_update, match):
    all_players_id = [player.id for player in Player.query.all()]
    # first update the match
    to_update.utcDate = match['utcDate']
    to_update.homeTeamScore = match.get('score').get(
        'fullTime').get('homeTeam')
    to_update.awayTeamScore = match.get('score').get(
        'fullTime').get('awayTeam')
    to_update.lastUpdated=match['lastUpdated']
    
    #if the match was scheduled more update is needed
    if to_update.status.name == "SCHEDULED":
        to_update.homeTeamCaptain_id = match.get('homeTeam').get('captain').get('id')
        to_update.awayTeamCaptain_id = match.get('awayTeam').get('captain').get('id')
        players = PopulateMatchesEvents.get_match_players(match)
        for player in players:
            if player.player_id in all_players_id:
                db.session.add(player)
    
    to_update.status = match.get("status")

    # get all match events
    events = PopulateMatchesEvents.get_match_events(match)
    # get all match subs
    subs = PopulateMatchesEvents.get_match_substitutions(match)
    # get all events from database
    dbEvents = Event.query.filter(Event.match_id == to_update.id).all()
    # get all substitutions from database
    dbSubs = MatchSubstitution.query.filter(MatchSubstitution.match_id == to_update.id).all()
    # delete all pervious events
    for event in dbEvents:
        db.session.delete(event)
    #delete all subs
    for sub in dbSubs:
        db.session.delete(sub)
    # add all new events
    for event in events:
        if event.player_id in all_players_id:
            db.session.add(event)
    for sub in subs:
        if sub.player_in_id in all_players_id and sub.player_out_id in all_players_id:
            db.session.add(sub)
    db.session.commit()

def perform_update():
    "Update matches and events"

    all_matches = Match.query
    all_players_id = [player.id for player in Player.query.all()]
    for competition in available_competitions:
        url = football_api["MatchEvent"] % competition
        headers = {}
        headers['X-Auth-Token'] = current_app.config['SOURCE_API_SECRET_KEY']
        resp = requests.get(url, headers=headers, verify=False)
        matches = resp.json()['data']
        for match in matches:
            # if the match is in the database already
            to_update = all_matches.filter(Match.id == match['id']).first()
            if to_update:
                # if it does not need update keep going
                if need_update(match, to_update) == False:
                    continue
                # if the match needs update
                else:
                    update_match_event(to_update, match)
                    continue
            else:
                # insert match players and events

                if match.get('status')!="SCHEDULED" and (match.get('homeTeam').get('captain').get('id') not in all_players_id or match.get('awayTeam').get('captain').get('id') not in all_players_id or match['status'] == 'POSTPONED'):
                    continue
                PopulateMatchesEvents.insert_match_event(match)
        print("%d is done from %d competitions"%(available_competitions.index(competition)+1, len(available_competitions)))
    
    return {"message":"All matches and events are updated"}
