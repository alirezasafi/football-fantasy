from flask_restplus import Namespace, fields

team_api = Namespace('Team', description="team related apis")

player_model = team_api.model(
    'player',{
        'id': fields.Integer(required=True),
        'name':fields.String(required=True, description='name of player'),
        'position':fields.String(required=True),
        'lineup': fields.Boolean(required=True, description="in lineup or not")
    }

)
pick_squad_model = team_api.model(
    'PickSquad',{
        'name':fields.String(required=True, description='name of squad'),
        'favorite_team':fields.String(),
        'budget': fields.Float(required=True),
        'captain':fields.Integer(required=True),
        'squad':fields.List(fields.Nested(player_model), required=True, description='a list of picked players')
    }

)

manage_team_model = team_api.model(
    'ManageSquad',{
        'squad':fields.List(fields.Nested(player_model), required=True, description='a list of picked players'),
        'captain':fields.Integer(required = True),
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
        'player_in': fields.Nested(transfer_player_model, required=True),
        'player_out': fields.Nested(transfer_player_model, required=True)
    }
)
fantasy_cards_model = team_api.model(
    'FantasyCards', {
        'card': fields.String(required=True, description="cards must be one of 'bench_boost', 'free_hit', 'triple_"
                                                         "captain', 'wild_card'"),
        'mode': fields.String(required=True, description="modes: 'active', 'inactive'"),
    }
)