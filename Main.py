import os
from typing import Optional, List
from datetime import date, datetime, time, timedelta
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, EmailStr
from fastapi import FastAPI, Depends
from fastapi_health import health
import motor.motor_asyncio
from pymongo import ReturnDocument
from Models.products import *

app = FastAPI(
    title="Amazon App"
)
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://kmickey1992:kAmmxxAz6jSn9hei@cluster0.bkux7zm.mongodb.net/?retryWrites=true&w=majority")
db = client.amazon
product_collection = db.get_collection("product")

# PyObjectId = Annotated[str, BeforeValidator(str)]

def get_session():
    return True


def is_database_online():
    return {"database": "online"}



app.add_api_route("/health", health([is_database_online]))

# class ProductModel(BaseModel):
#     """
#     Container for a single product record.
#     """
#     productid: Optional[int]
#     name: Optional[str]
#     category: Optional[str]
#     price: Optional[float]
#     created_at: Optional[datetime]
#
# class UpdateProductModel(BaseModel):
#     """
#     Container for a single Product record.
#     """
#     name: Optional[str]
#     category: Optional[str]
#     price: Optional[float]
#     created_at: Optional[datetime]
#
# class ProductCollection(BaseModel):
#     """
#     Container for a single product record.
#     """
#     product:List[ProductModel]

@app.post("/product/"  ,response_description="Add new product",
response_model=ProductModel,
status_code=status.HTTP_201_CREATED,
response_model_by_alias=False,)

async def create_product(product: ProductModel= Body(...)):
    """
    Insert a new product record.

    A unique `id` will be created and provided in the response.
    """
    new_product=await product_collection.insert_one(product.model_dump(by_alias=True))
    return product

@app.get(
    "/product/",
    response_description="List all product",
    response_model=ProductCollection,
    response_model_by_alias=False,
)
async def list_product():
    """
    List all of the product data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return ProductCollection(product=await product_collection.find().to_list(1000))

@app.delete("/product/{productid}", response_description="Delete a product")
async def delete_product(productid: int):
    """
    Remove a single product record from the database.
    """
    print("here is the product id",productid)
    delete_result = await product_collection.delete_many({"productid": productid})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    elif delete_result.deleted_count != 1:
        return Response(status_code=200)

    raise HTTPException(status_code=404, detail=f"Product {productid} not found")

@app.put(
    "/product/{productid}",
    response_description="Update a product",
    response_model=ProductModel,
    response_model_by_alias=False,
)
async def update_product(productid: int, product: UpdateProductModel = Body(...)):
    """
    Update individual fields of an existing product record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    product = {
        k: v for k, v in product.model_dump(by_alias=True).items() if v is not None
    }
    if len(product) >= 1:
        update_result = await product_collection.find_one_and_update(
            {"productid": productid},
            {"$set": product},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Product {productid} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_product := await product_collection.find_one({"productid": productid})) is not None:
        return existing_product

    raise HTTPException(status_code=404, detail=f"Product {productid} not found")
