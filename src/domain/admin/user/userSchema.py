from ...schemas.user_schema import UserBase
from ...schemas.pagination_schema import PaginationBase

class ResponseSiswaPag(PaginationBase) :
    data : list[UserBase] = []