from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_records: int
    total_pages: int


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"
    error: Optional[Any] = None
    meta: Optional[PaginationMeta] = None
