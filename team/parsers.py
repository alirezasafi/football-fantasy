from flask_restplus import reqparse


PickSquad_parser = reqparse.RequestParser()
PickSquad_parser.add_argument('squad-name', required=True)
PickSquad_parser.add_argument('picks', type=dict, action='append', required=True)
PickSquad_parser.add_argument('favourite-team')
PickSquad_parser.add_argument('captain-id', required=True)

ManageTeam_parser = reqparse.RequestParser()
ManageTeam_parser.add_argument('squad', type=dict, action='append', required=True)
ManageTeam_parser.add_argument('captain-id', required=True)