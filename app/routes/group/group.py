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
Group = models.Group
GroupMember = models.GroupMember

class GroupModel(BaseModel):
    g_name: str
    g_motor: str
    g_description: str
    g_image_url: str
    g_content_type: str
    g_member_type: str
    g_allow_gender: str
    g_limit_member: int
    g_invite_option: int
    g_non_member: bool
    g_status: bool

class GroupMemberModel(BaseModel):
    g_id: int
    u_id: int
    g_role: bool

@router.post('/start_group/{user_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Group"],
    include_in_schema=True,
    description="Start your group and Create a group member",
)
def start_group(user_name: str, GroupModel: GroupModel, session: Session = Depends(get_session)):
    # Get User ID
    query = select(User).where(
        User.u_name == user_name
    )
    query_user = session.exec(query).first()
    if query_user is None:
        return {'Status': 'Success', 'Response': 'Sign Up First'}
    
    # Check whether Group is existance or not
    query = select(Group).where(
        Group.g_name == GroupModel.g_name
    )
    query_group = session.exec(query).first()
    if query_group is not None:
        return {'Status': 'Success', 'Response': 'Group Name is already existed'}

    # Create a Group
    try:
        new_group = Group(
            g_name = GroupModel.g_name,
            g_motor = GroupModel.g_motor,
            g_description = GroupModel.g_description,
            g_image_url = GroupModel.g_image_url,
            g_content_type = GroupModel.g_content_type,
            g_member_type = GroupModel.g_member_type,
            g_allow_gender = GroupModel.g_allow_gender,
            g_limit_member = GroupModel.g_limit_member,
            g_invite_option = GroupModel.g_invite_option
        )
        session.add(new_group)
        session.commit()
    except:
        return {'Status': 'Fail', 'Response': 'Failed to Create a Group'}

    # Create a GroupMember
    try:
        new_group_member = GroupMember(
            g_id = new_group.g_id,
            u_id = query_user.u_id
        )
        session.add(new_group_member)
        session.commit()

        # Update Group with the Group Memember ID
        new_group.gm_id = new_group_member.gm_id
        session.add(new_group)
        session.commit()
        session.refresh(new_group)

        return {'Status': 'Success', 'Response': {'group_id': new_group.g_id, 'group_member_id': new_group_member.gm_id}}
    except:
        return {'Status': 'Fail', 'Response': 'Failed to Create a Group Member'}

@router.get('/show_groups',
    dependencies=[Depends(bearer.has_access)],
    tags=["Group"],
    include_in_schema=True,
    description="Show all the groups",
)
def show_groups(session: Session = Depends(get_session)):
    query = select(Group)
    query_groups = session.exec(query)

    groups = []
    for group in query_groups:
        group_info = {}
        group_info['name'] = group.g_name
        group_info['motor'] = group.g_description
        group_info['image_url'] = group.g_image_url

        groups.append(group_info)
    
    return {'Status': 'Success', 'Response': groups}