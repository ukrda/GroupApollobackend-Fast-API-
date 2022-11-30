import os
import fastapi
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from sqlmodel import Session, select
from pydantic import BaseModel
import random

from app.database.db import get_session, get_engine
from app.models.models import User, Group, GroupMember
from app.models.basemodels import UserModel, GroupModel
from app.security import bearer

load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = get_engine()


@router.post('/start_group',
             dependencies=[Depends(bearer.get_current_active_user)],
             tags=["Group"],
             include_in_schema=True,
             description="Start your group and Create a group member",
             )
def start_group(GroupModel: GroupModel, current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    print("Groupmodel = ", GroupModel)
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
            g_name=GroupModel.g_name,
            g_motor=GroupModel.g_motor,
            g_description=GroupModel.g_description,
            g_image_url=GroupModel.g_image_url,
            g_content_type=GroupModel.g_content_type,
            g_member_type=GroupModel.g_member_type,
            g_allow_gender=GroupModel.g_allow_gender,
            g_limit_member=GroupModel.g_limit_member,
            g_invite_option=GroupModel.g_invite_option
        )
        session.add(new_group)
        session.commit()
    except:
        return {'Status': 'Fail', 'Response': 'Failed to Create a Group'}

    # Create a GroupMember
    try:
        new_group_member = GroupMember(
            g_id=new_group.g_id,
            u_id=current_user.u_id
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
            dependencies=[Depends(bearer.get_current_active_user)],
            tags=["Group"],
            include_in_schema=True,
            description="Show all the groups",
            )
def show_groups(current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    # Get GroupMember ID
    query = select(GroupMember).where(
        GroupMember.u_id != current_user.u_id,
        GroupMember.g_role == True
    )
    query_group_member = session.exec(query).all()

    groups = []
    for group_member in query_group_member:
        query = select(Group).where(
            Group.gm_id == group_member.gm_id
        )
        query_groups = session.exec(query).all()

        for group in query_groups:
            group_info = {}
            group_info['name'] = group.g_name
            group_info['motor'] = group.g_description
            group_info['image_url'] = group.g_image_url
            group_info['is_invite_only'] = group.g_invite_option
            group_info['is_group_owner'] = group_member.g_role
            group_info['group_status'] = group.g_status
            groups.append(group_info)

    if len(groups) == 0:
        return {'Status': 'Success', 'Response': groups}
    else:
        return {'Status': 'Success', 'Response': groups}


@router.get('/show_own_groups',
            dependencies=[Depends(bearer.get_current_active_user)],
            tags=["Group"],
            include_in_schema=True,
            description="Show your own groups",
            )
def show_own_group(request: Request, current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):

    # Get GroupMember ID
    query = select(GroupMember).where(
        GroupMember.u_id == current_user.u_id,
    )
    query_group_member = session.exec(query).all()

    # if len(query_group_member) == 0:
    #     # redirect_url = request.url_for('user_profile', **{ 'pk' : pk})
    #     redirect_url = request.url_for('show_groups', **{ 'option' : 1})
    #     return RedirectResponse(redirect_url)

    groups = []
    for group_member in query_group_member:
        query = select(Group).where(
            Group.gm_id == group_member.gm_id
        )
        query_groups = session.exec(query).all()

        for group in query_groups:
            group_info = {}
            group_info['name'] = group.g_name
            group_info['motor'] = group.g_description
            group_info['image_url'] = group.g_image_url
            group_info['is_invite_only'] = group.g_invite_option
            group_info['is_group_owner'] = group_member.g_role
            groups.append(group_info)

    return {'Status': 'Success', 'Response': groups}


def get_sort_by_query(sort_by, u_id):
    if sort_by == 1:
        query = ''
    elif sort_by == 2:
        query = ''


# @router.get('/show_member_groups/{sort_by}/{show_options}',
@router.get('/show_member_groups',
            dependencies=[Depends(bearer.get_current_active_user)],
            tags=["Group"],
            include_in_schema=True,
            description="Show your member groups",
            )
# def show_member_group(sort_by: int, show_options: str, current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
def show_member_group(current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    query_member_group = select(GroupMember).where(
        GroupMember.u_id == current_user.u_id
    )
    query_group = session.exec(query_member_group).all()

    print("---------------", query_group)

    groups = []
    for group_member in query_group:
        query = select(Group).where(
            Group.g_id == group_member.g_id
        )
        query_groups = session.exec(query).all()

        for group in query_groups:
            group_info = {}
            group_info['name'] = group.g_name
            group_info['motor'] = group.g_description
            group_info['image_url'] = group.g_image_url
            group_info['is_invite_only'] = group.g_invite_option
            group_info['is_group_owner'] = group_member.g_role
            groups.append(group_info)

    return {'Status': 'Success', 'Response': groups}

@router.get('/show_specific_group/{group_name}',
            dependencies=[Depends(bearer.get_current_active_user)],
            tags=["Group"],
            include_in_schema=True,
            description="Show your specific group info",
            )
def show_specific_group(group_name: str, current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    query_group_info = select(Group).where(
        Group.g_name == group_name
    )

    group_info = session.exec(query_group_info).first()

    return group_info
