from pydantic import BaseModel

class Venue(BaseModel):
    Community:str
    Address: str
    Price: str
    Sqft:int
    Beds: int
    Baths: int
    Garage: int
    Stories: int
    Lot: str

