from .constants import admin_password, admin_username, competitions, admin_token, squad_data
from .auth import RegisterTasks, LoginTasks
from .player import CompetitionPlayerTasks
from .team import PickSquadTasks, GetManageTeamTask, CardsTasks
from .transfer import TransferTasks
from .statistics import PlayerStatisticsTasks, SquadStatistics
from .match import CurrentWMTasks, MatchDetailTasks
from .competition import CompetitionTasks
from .club import ClubTasks
from .profile import ProfileTasks
