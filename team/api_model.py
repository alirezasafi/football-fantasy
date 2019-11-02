from flask_restplus import Namespace, fields

team_api = Namespace('team', description="team related apis")

position_player_model = team_api.model(
    'position_player',{
        'player_id': fields.Integer(required=True),
        'player':fields.String(required=True, description='name of player'),
        'position':fields.String(required=True),
        'lineup': fields.Boolean(required=True, description="in lineup or not")
    }

)
pick_squad_model = team_api.model(
    'PickSquad',{
        'squad-name':fields.String(required=True, description='name of squad'),
        'favorite-team':fields.String(),
        'budget': fields.Float(required=True),
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
transfer_player_model = team_api.model(
    'TransferPlayer', {
        'id': fields.Integer(requied=True),
        'name': fields.String(required=True)
    }
)
transfer_model = team_api.model(
    "Transfer", {
        'player_in': fields.Nested(transfer_player_model, required=True)
    }
)