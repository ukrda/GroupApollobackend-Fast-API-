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
Stream = models.Stream

class StreamModel(BaseModel):
    s_content_type: int
    s_title: str
    s_media_path: str

@router.post('/start_stream/{group_name}/{user_name}',
    dependencies=[Depends(bearer.has_access)],
    tags=["Stream"],
    include_in_schema=True,
    description="Start your stream",
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
