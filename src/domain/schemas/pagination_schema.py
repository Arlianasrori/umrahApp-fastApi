from pydantic import BaseModel

class PaginationBase(BaseModel):
    count_data : int
    count_page : int