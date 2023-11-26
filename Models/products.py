from pydantic import  BaseModel
from typing import Optional, List
from datetime import date, datetime, time, timedelta

class ProductModel(BaseModel):
    """
    Container for a single product record.
    """
    productid: Optional[int]
    name: Optional[str]
    category: Optional[str]
    price: Optional[float]
    created_at: Optional[datetime]

class UpdateProductModel(BaseModel):
    """
    Container for a single Product record.
    """
    name: Optional[str]
    category: Optional[str]
    price: Optional[float]
    created_at: Optional[datetime]

class ProductCollection(BaseModel):
    """
    Container for a single product record.
    """
    product:List[ProductModel]