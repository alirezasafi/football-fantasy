from flask_restplus import Namespace, fields

team_api = Namespace('team', description="team related apis")

position_player_model = team_api.model(
    'position_player',{
        'player':fields.String(required=True, description='name of squad'),
        'position':fields.String(required=True)
    }

)
pick_squad_model = team_api.model(
    'PickSquad',{
        'squad-name':fields.String(required=True, description='name of squad'),
        'favorite-team':fields.String(),
        'captain-id':fields.Integer(required = True),
        'picks':fields.List(fields.Nested(position_player_model), required=True, description='a list of picked players')
    }

)

manage_team_model = team_api.model(
    'ManageSquad',{
        'squad':fields.List(fields.Nested(position_player_model), required=True, description='a list of picked players'),
        'captain-id':fields.Integer(required = True),
    }

)