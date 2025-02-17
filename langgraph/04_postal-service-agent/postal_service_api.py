def create_mailing_order_stubbed(recipient: str, address: str, package_type: str):
    if not recipient or not address or not package_type:
        status = 'Failure'
        message = 'Mailing Order Creation Failed; Reason: All Required Information is not supplied'

        print(status)
        print(message)

        return status, message
        
    else:
        status = 'Success'
        message = 'Mailing Order Created Successfully'
        tracking_number = 'MAIL123456'

        print(status)
        print(message)
        print(tracking_number)
        
        return status, message, tracking_number
    
def create_shipment_order_stubbed(recipient: str, address: str, package_type: str):
    """ Create a shipment order """

    if not recipient or not address or not package_type:
        status = 'Failure'
        message = 'Shipment Order Creation Failed; Reason: All Required Information is not supplied'

        print(status)
        print(message)

        return status, message
        
    else:
        status = 'Success'
        message = 'Shipment Order Created Successfully'
        tracking_number = 'SHIP123456'
        
        print(status)
        print(message)
        print(tracking_number)
        
        return status, message, tracking_number
    
def get_api_specs_stubbed(order_category: str):
    """ Get API Specifications for Mailing or Shipment Order. The order creation request should honor these request specifications in order to successfully create an order. """

    print(["recipient", "address", "package_type"])

    return ["recipient", "address", "package_type"]

def validate_order_stubbed(recipient: str, address: str, package_type: str):
    """ Determine if the order creation request is valid by checking if all required values have been supplied """

    if not recipient or not address or not package_type:
        print("Order creation request is invalid")
        return "Order creation request is invalid"
    else: 
        print("Order creation request is valid")
        return "Order creation request is valid"