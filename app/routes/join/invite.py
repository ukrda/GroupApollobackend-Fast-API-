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
InvitationLog = models.InvitationLog

class InvitationLogModel(BaseModel):
    c_id: str
    i_note: str
    i_status: int

@router.post('/send_invite/{group_name}/{manager_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Join"],
    include_in_schema=True,
    description="Send an invitation to join",
)
def send_invite(group_name: str, manager_name: str, InvitationLogModel: InvitationLogModel, session: Session = Depends(get_session)):
    # Get GroupMember ID to be invited
    query = select(Group).where(
        Group.g_name == group_name
    )
    query_group = session.exec(query).first()

    query = select(User).where(
        User.u_name == manager_name
    )
    query_user = session.exec(query).first()

    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.u_id == query_user.u_id
    )
    query_group_member = session.exec(query).first() # manager

    # Get Invitee's ID
    query = select(User).where(
        User.u_name == InvitationLogModel.c_id
    )
    query_invitee = session.exec(query).first()
    if query_invitee is None:
        return {'Status': 'Success', 'Response': 'No such a User'}

    # Create a Invitation log
    try:
        new_invitation = InvitationLog(
            c_id = query_invitee.u_id,
            i_note = InvitationLogModel.i_note,
            i_status = InvitationLogModel.i_status,
            gm_id = query_group_member.gm_id
        )
        session.add(new_invitation)
        session.commit()

        return {'Status': 'Success', 'Response': new_invitation.i_id}
    except:
        return {'Status': 'Fail', 'Response': 'Fail to create an invitation'}

@router.get('/check_invite/{user_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Join"],
    include_in_schema=True,
    description="Check the invitation on the User Member side",
)
def check_invite(user_name: str, session: Session = Depends(get_session)):
    # Get the User's ID
    query = select(User).where(
        User.u_name == user_name
    )
    query_user = session.exec(query).first()

    # Check invitation
    query = select(InvitationLog).where(
        InvitationLog.c_id == query_user.u_id,
        InvitationLog.i_status == 0
    )
    query_invitations = session.exec(query)
    invitations = []
    for invitation in query_invitations:
        query = select(GroupMember).where(
            GroupMember.gm_id == invitation.gm_id
        )
        query_group_member = session.exec(query).first()

        query = select(Group).where(
            Group.g_id == query_group_member.g_id
        )
        query_group = session.exec(query).first()

        query = select(User).where(
            User.u_id == query_group_member.u_id
        )
        query_manager = session.exec(query).first()

        invitation_user = {}
        invitation_user['group_name'] = query_group.g_name
        invitation_user['group_motor'] = query_group.g_motor
        invitation_user['group_limited_member'] = query_group.g_limit_member
        invitation_user['group_invite_option'] = query_group.g_invite_option
        invitation_user['group_manager'] = query_manager.u_name

        invitations.append(invitation_user)
    
    return {'Status': 'Success', 'Response': invitations}
