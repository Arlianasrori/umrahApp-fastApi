from pydantic import BaseModel
from ...utils.generateId_util import generate_id

class AddNotificationModel(BaseModel):
    id : int = generate_id()
    user_id : int
    title : str
    body : str

