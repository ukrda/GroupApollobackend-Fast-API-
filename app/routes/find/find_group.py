import fastapi
from fastapi import Depends
from dotenv import load_dotenv
from sqlmodel import Session, select, text

from app.database.db import get_session, get_engine
from app.models.models import Group, GroupMember
from app.models.basemodels import FindGroup
from app.security import bearer

load_dotenv()

router = fastapi.APIRouter()

engine = get_engine()

@router.post('/find_group',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Find"],
    include_in_schema=True,
    description="Find Groups to Join",
)
def find_group(find_option: FindGroup, session: Session = Depends(get_session)):
    query = 'Group.g_name == ' + find_option.group_name + ', ' + 'Group.g_description == ' + find_option.group_description + 'Group.g_member_type == 1, '
    return find_option

    """SELECT groupmember.gm_id AS gmId, count(groups.gm_id) AS aaa FROM groupmember 
left join groups on groupmember.gm_id = groups.gm_id where groupmember.g_role = True and groups.g_description = 'auth_test'
group by gmId having count(groups.gm_id) >= 1"""