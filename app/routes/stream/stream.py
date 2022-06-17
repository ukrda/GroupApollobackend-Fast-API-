import os
import fastapi
from fastapi import Depends, UploadFile, File
from dotenv import load_dotenv
from sqlmodel import Session, select
from pydantic import BaseModel
import aiofiles

from datetime import datetime

from app.database.db import get_session, get_engine
from app.models import models
from app.security import bearer



load_dotenv()
salt = os.environ["Foreign_key_salt"]
static_directory = os.environ['Static_file']

router = fastapi.APIRouter()

engine = get_engine()

User = models.User
GroupMember = models.GroupMember
Group = models.Group
Stream = models.Stream

class StreamModel(BaseModel):
    s_content_type: int
    s_title: str
    s_media_path: str

@router.post('/start_stream/{group_name}/{user_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Stream"],
    include_in_schema=True,
    description="Post your stream",
)
def start_stream(group_name: str, user_name: str, StreamModel: StreamModel, session: Session = Depends(get_session)):
    # Get GroupMember ID and Group ID & User ID
    query = select(Group).where(
        Group.g_name == group_name
    )
    query_group = session.exec(query).first()
    if query_group is None:
        return {'Status': 'Success', 'Response': 'No such a group'}

    query = select(User).where(
        User.u_name == user_name
    )
    query_user = session.exec(query).first()
    if query_user is None:
        return {'Status': 'Success', 'Response': 'No such a user'}

    query = select(GroupMember).where(
        GroupMember.g_id == query_group.g_id,
        GroupMember.u_id == query_user.u_id
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

@router.get('/show_stream/{user_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Stream"],
    include_in_schema=True,
    description="Show your stream",
)
def show_stream(user_name: str, session: Session = Depends(get_session)):
    # Get User ID
    query = select(User).where(
        User.u_name == user_name
    )
    query_user = session.exec(query).first()

    # Get Group Member
    query = select(GroupMember).where(
        GroupMember.u_id == query_user.u_id
    )
    query_group_member = session.exec(query)
    streams = []
    for group_member in query_group_member:
        stream_info = {}
        
        query = select(Group).where(
            Group.g_id == group_member.g_id
        )
        query_group = session.exec(query).first()

        query = select(Stream).where(
            Stream.gm_id == group_member.gm_id
        )
        query_stream = session.exec(query).first()

        stream_info['group_name'] = query_group.g_name
        stream_info['stream_title'] = query_stream.s_title
        stream_info['stream_content_type'] = query_stream.s_content_type
        stream_info['s_media_path'] = query_stream.s_media_path

        streams.append(stream_info)
    
    return {'Status': 'Success', 'Response': streams}

@router.post('/upload_stream',
    dependencies=[Depends(bearer.has_access)],
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
    
    return {'Status': 'Success', 'Response': upload_stream.file}