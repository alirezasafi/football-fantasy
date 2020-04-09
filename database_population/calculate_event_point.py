from .globals import rules


def calculate_event_point(event, matchplayer):
    point = 0

    if event.event_type == 'YELLOW_CARD':
        
        point += rules['yellowCard']
    elif event.event_type == 'RED_CARD' or event.event_type == 'YELLOW_RED_CARD':
        point += rules['redCard']
    elif event.event_type == 'GO':
        if matchplayer.player.position.name == 'Goalkeeper' or matchplayer.player.position.name == 'Defender':
            point += rules['DefGKGoal']
        elif matchplayer.player.position.name == 'Midfielder':
            point += rules['MidGoal']
        else:
            point += rules['FWGoal']
    elif event.event_type == 'AS':
        point += rules['assist']
    elif event.event_type == 'OWNGO':
        point += rules['ownGoal']
    return point