from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    u_name: str
    u_password: str
    u_email: str
    
class TokenModel(BaseModel):
    code: str
    code_verifier: str

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

class StreamModel(BaseModel):
    s_content_type: Optional[int] = 1
    s_title: str
    s_media_path: str

class FindGroup(BaseModel):
    group_name: str
    group_description: str
    new_member: bool
    custodian: int
    from_member: int
    to_member: int
    percentage: float
    more_than: int
    post_day: int