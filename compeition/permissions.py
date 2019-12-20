from functools import wraps
from .models import Competition
from werkzeug.exceptions import NotFound


def has_competition(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        competition_id = kwargs['competition_id']
        competition = Competition.query.filter_by(id=competition_id).first()
        if not competition:
            raise NotFound(description="competition not found!!")
        return f(*args, **kwargs)
    return decorated_function
