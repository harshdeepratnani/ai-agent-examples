from pydantic import BaseModel, Field

class TravelOptionRequest(BaseModel):
    """ Request for travel options """
    origin: str = Field(description="Origin of the travel", min_length=3, max_length=50)
    destination: str = Field(description="Destination of the travel", min_length=3, max_length=50)
    # departure_date: str = Field(description="Departure date", pattern="^\d{4}-\d{2}-\d{2}$")
    # return_date: str = Field(description="Return date", pattern="^\d{4}-\d{2}-\d{2}$")

class Option(BaseModel):
    """ Travel options """
    option: str = Field(description="Travel option")
    price: float = Field(description="Price of the travel option")
    departure_time: str = Field(description="Departure time")
    arrival_time: str = Field(description="Arrival time")

class TravelOptionResponse(BaseModel):
    """ Response for travel options """
    options: list[Option] = Field(description="List of travel options")

class WalletBalance(BaseModel):
    """ Wallet balance """
    balance: float = Field(description="Wallet balance")

class BookTravelResponse(BaseModel):
    """ Book travel response """   
    booking_id: str = Field(description="Booking ID")
    status: str = Field(description="Booking status")

def get_travel_options_stubbed(travel_option_request: TravelOptionRequest):
    """ Stubbed API call to get travel options """
    
    options = [
        Option(option="Train", price=100.0, departure_time="10:00", arrival_time="23:00"),
        Option(option="Bus", price=200.0, departure_time="00:00", arrival_time="23:00"),
        Option(option="Flight", price=300.0, departure_time="14:00", arrival_time="16:00")
    ]
    return TravelOptionResponse(options=options)

def check_wallet_balance_stubbed():
    """ Stubbed API call to check wallet balance """
    
    return WalletBalance(balance=500.0)

def book_travel_stubbed(option: Option):
    """ Stubbed API call to book travel """
    
    return BookTravelResponse(booking_id="12345", status="Success")