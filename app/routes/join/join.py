import os
import fastapi
from fastapi import Depends
from dotenv import load_dotenv
from sqlmodel import Session, select
from pydantic import BaseModel

from app.database.db import get_session, get_engine
from app.models import models
from app.security import bearer

load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = get_engine()

User = models.User
GroupMember = models.GroupMember
Group = models.Group
Join = models.Join

class JoinModel(BaseModel):
    user_name: str
    group_name: str

@router.post('/send_join',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Join"],
    include_in_schema=True,
    description="Send a request to join",
)
def send_join(join: JoinModel, session: Session = Depends(get_session)):
    query = select(Group).where(
        Group.g_name == join.group_name
    )
    query_group = session.exec(query).first()

    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.g_role == True
    )
    query_group_member = session.exec(query).first()

    query = select(User).where(
        User.u_name == join.user_name
    )
    query_user = session.exec(query).first()

    # Create a Join Request
    try:
        new_join_request = Join(
            u_id = query_user.u_id,
            gm_id = query_group_member.gm_id,
            join_status = 1
        )
        session.add(new_join_request)
        session.commit()

        return {'Status': 'Success', 'Response': new_join_request.j_id}
    except:
        return {'Status': 'Fail', 'Response': 'Failed to send a join request'}

@router.get('/check_join/{group_name}',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Join"],
    include_in_schema=True,
    description="Check the join requests on the Group Manager side",
)
def check_join(group_name: str, session: Session = Depends(get_session)):
    query = select(Group).where(
        Group.g_name == group_name
    )
    query_group = session.exec(query).first()
    
    # Get Group Manager
    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.g_role == True
    )
    query_group_manager = session.exec(query).first()

    # Check Join Requests
    query = select(Join).where(
        Join.gm_id == query_group_manager.gm_id,
        Join.join_status == 1
    )
    join_requests = session.exec(query)

    joins = []
    for join_req in join_requests:
        query = select(User).where(
            User.u_id == join_req.u_id
        )
        query_user = session.exec(query).first()

        join_user = {}
        join_user['user_name'] = query_user.u_name
        joins.append(join_user)

    return {'Status': 'Success', 'Response': joins}

@router.post('/accept_join/{group_name}/{user_name}',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Join"],
    include_in_schema=True,
    description="Decide whether join request is accepted or declined on the Group Manager side",
)
def decide_join(group_name: str, user_name: str, status: int, session: Session = Depends(get_session)):
    # Get User Id
    query = select(User).where(
        User.u_name == user_name
    )
    query_user = session.exec(query).first()

    # Get Group Manager
    query = select(Group).where(
        Group.g_name == group_name
    )
    query_group = session.exec(query).first()

    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.g_role == True
    )
    query_group_member = session.exec(query).first()

    # Update Join
    query = select(Join).where(
        Join.u_id == query_user.u_id,
        Join.gm_id == query_group_member.gm_id
    )
    query_join = session.exec(query).first()

    try:
        query_join.join_status = status
        session.add(query_join)
        session.commit()
        session.refresh(query_join)

        # Add a Group Member
        try:
            new_group_member = GroupMember(
                g_id = query_group.g_id,
                u_id = query_user.u_id,
                g_role = False
            )
            session.add(new_group_member)
            session.commit()

            return {'Status': 'Success', 'Response': new_group_member.g_id}
        except:
            return {'Status': 'Fail', 'Response': 'Fail to add a new group member'}
    except:
        return {'Status': 'Fail', 'Response': 'Faile to accept a join request'}