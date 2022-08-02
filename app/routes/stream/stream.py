import os
import fastapi
from fastapi import Depends, UploadFile, File
from dotenv import load_dotenv
from sqlmodel import Session, select, text
from pydantic import BaseModel
import aiofiles
from typing import Union

import datetime

from app.database.db import get_session, get_engine
from app.models.models import User, Group, GroupMember, Stream
from app.models.basemodels import UserModel, StreamModel
from app.security import bearer

load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = get_engine()

@router.post('/start_stream/{group_name}',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Stream"],
    include_in_schema=True,
    description="Post your stream",
)
def start_stream(group_name: str, StreamModel: StreamModel, current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    # Get GroupMember ID and Group ID & User ID
    query = select(Group).where(
        Group.g_name == group_name
    )
    query_group = session.exec(query).first()
    if query_group is None:
        return {'Status': 'Success', 'Response': 'No such a group'}

    # query = select(User).where(
    #     User.u_name == current_user.u_name
    # )
    # query_user = session.exec(query).first()
    # if query_user is None:
    #     return {'Status': 'Success', 'Response': 'No such a user'}

    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.u_id == current_user.u_id
    )
    query_group_member = session.exec(query).first()
    if query_group_member is None:
        return {'Status': 'Success', 'Response': 'User is not a member of this group'}

    # Create a Stream
    try:
        new_stream = Stream(
            s_content_type = StreamModel.s_content_type,
            s_title = StreamModel.s_title,
            s_media_path = StreamModel.s_media_path,
            gm_id = query_group_member.gm_id
        )
        session.add(new_stream)
        session.commit()

        return {'Status': 'Success', 'Response': new_stream.s_id}
    except:
        return {'Status': 'Fail', 'Response': 'Failed to Create a Stream'}

def query_show_option(options: str) -> str:
    number_of_options = len(options)
    query = ''
    for index in range(number_of_options):
        if options[index] == '1':
            query += 'Stream.s_content_type = 1 OR '
        elif options[index] == '2':
            query += 'Stream.s_content_type = 2 OR '
        elif options[index] == '3':
            query += 'Stream.s_content_type = 3 OR '
        elif options[index] == '4':
            query += 'Stream.s_content_type = 4 OR '
        elif options[index] == '5':
            query += 'Stream.s_content_type = 5'
    
    return query

@router.get('/show_stream/{view_mode}/{show_options}',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Stream"],
    include_in_schema=True,
    description="Show your stream",
)
def show_stream(view_mode: Union[int, None] = None, show_options: Union[str, None] = '12345',  current_user: UserModel = Depends(bearer.get_current_active_user), session: Session = Depends(get_session)):
    # # Get User ID
    # query = select(User).where(
    #     User.u_name == user_name
    # )
    # query_user = session.exec(query).first()

    # # Get Group Member
    # query = select(GroupMember).where(
    #     GroupMember.u_id == query_user.u_id
    # )

    # query = select(User, GroupMember).where(
    #     User.u_name == current_user.u_name,
    #     User.u_id == GroupMember.u_id
    # )

    query = select(Group).where(
        GroupMember.u_id == current_user.u_id
    )
    query_group_member = session.exec(query).all()
    streams = []
    for group_member in query_group_member:
        stream_info = {}
        query = select(Group).where(
            Group.g_id == group_member.g_id
        )
        query_group = session.exec(query).first()

        # query = select(Stream).where(
        #     Stream.gm_id == group_member.gm_id
        # )
        # query_stream = session.exec(query).all()

        
        # query = ''
        query = query_show_option(show_options)
        if query == '':
            query = 'Stream.gm_id = ' + str(group_member.gm_id)
        else:
            query = 'Stream.gm_id = ' + str(group_member.gm_id) + ' AND ' + query
        query_stream = session.query(Stream).filter(text(query))

        if query_group is not None:
            for stream in query_stream:
                stream_info['group_name'] = query_group.g_name
                stream_info['stream_title'] = stream.s_title
                stream_info['stream_content_type'] = stream.s_content_type
                stream_info['s_media_path'] = stream.s_media_path
                stream_info['posted_time_ago'] = datetime.datetime.now() - stream.s_created_timestamp

                streams.append(stream_info)
    
    return {'Status': 'Success', 'Response': streams}

@router.post('/upload_stream',
    dependencies=[Depends(bearer.get_current_active_user)],
    tags=["Stream"],
    include_in_schema=True,
    description="Upload your stream",
)
async def upload_stream(upload_stream: UploadFile=File()):
    upload_file_path = os.path.join('static/', upload_stream.filename)
    async with aiofiles.open(upload_file_path, 'wb') as out_file:
        content = await upload_stream.read(1024)
        while content:  # async read chunk
            await out_file.write(content)  # async write chunk
            content = await upload_stream.read(1024)
    
    return {'Status': 'Success', 'Response': upload_stream.filename}