from werkzeug.exceptions import HTTPException


class SquadException(HTTPException):
    code = 400
    description = "select a squad with 15 players, consisting of: 2 Goalkeepers, 5 Defenders, 5 Midfielders, 3 Forwards"


class FormationException(HTTPException):
    code = 400
    description = "select your lineup players providing that 1 goalkeeper, at least 3 defenders and at least " \
                  "1 forward are. "



