from django.shortcuts import render
from json.decoder import JSONDecodeError
from django.http import JsonResponse, HttpRequest
import json

# delivery cost by distance
DELIVERY_COST_SLAB = {
    (0, 10000): 5000,
    (10000, 20000): 10000,
    (20000, 50000): 50000,
    (50000, 500000): 100000
}

# Reason phrases for http status codes
STATUS_CODE_REASON_PHRASE = {
    400: "Bad Request",
    500: "Internal Server Error",
    501: "Not Implemented"
}

def create_HTTP_error_message(status_code: int, description: str) -> dict:
    """
    Creates a dictionary for the error message with appropriate details
    @params:
        status_code {int} -> HTTP status code of the message,
        description {str} -> possible reason for the error
    @returns:
        A dictionary object with appropriate details 
    """
    return {
        "status code": status_code,
        "error message": STATUS_CODE_REASON_PHRASE.get(status_code),
        "description": description
    }

def get_price(request: HttpRequest) -> JsonResponse:
    """
    API View for handling GET/POST request on '/'.
    @params:
        request {HttpRequest} ->  request object of GET/POST method.
    @returns:
        JsonResponse object.
    """

    # if method is GET return html template
    if request.method == "GET":
        return render(request, "Main/index.html")

    try:
        # if HTTP method is not POST then return 501 error
        assert request.method == "POST", create_HTTP_error_message(501, "Only HTTP POST method is accepted for calculating the total order cost :/")
        
        ###################### Loading JSON payload #######################

        # getting the payload file from the POST request form-data body
        payload = request.FILES.get("payload")

        if payload is not None:
            # if payload file is not JSON, return 400 error.
            if payload.content_type != "application/json":
                raise Exception(create_HTTP_error_message(400, f"{payload} is not a JSON file! please provide a valid JSON file with '.json' extension"))
            # if payload exists, load it into 'data' as JSON.
            # may return JSONDecodeError, if JSON syntax is violated!
            data = json.loads(payload.read())
        else:
            # if no payload returns 400 error message
            raise Exception(create_HTTP_error_message(400, "JSON file with filename as 'payload' is missing in the form-data!"))


        ###################### Extracting order items, distance and offer(if any) ##########################

        orders = data.get("order_items")
        distance = data.get("distance")
        offer = data.get("offer")

        items_price, delivery_cost, offer_amount = 0, 0, 0
        
        # if 'order-items' or 'distance' keys donot exists in the payload, return 400 error
        assert (orders is not None and distance is not None), create_HTTP_error_message(400, "either 'order_items' or 'distance' attributes are missing in the json")
        
        ######################### Calculating the total order price #############################

        for item in orders:
            # checking if item object have quantity and price data.
            assert item.get("quantity") and item.get("price"), create_HTTP_error_message(400, "either quantity or price are missing from an item")

            # if exists, add their product to the total items_price
            items_price += item.get("quantity") * item.get("price")

        # getting the delivery cost by distance using DELIVERY_COST_SLAB hash table
        for key in DELIVERY_COST_SLAB:
            if key[0] <= distance < key[1]:
                delivery_cost = DELIVERY_COST_SLAB[key]
                break
        
        ############################# Calculating discount and final price #########################################
        
        # if offer is applicable, get offer amount
        if offer is not None:
            offer_type = offer["offer_type"].lower()
            if offer_type == "flat":
                offer_amount = offer["offer_val"]
            elif offer_type == "delivery":
                offer_amount = delivery_cost
            else:
                raise Exception(create_HTTP_error_message(
                    400,
                    "Invalid offer type!"
                ))

        # calculate the total order without offer
        order_total_without_offer = items_price + delivery_cost

        # calculate discount and total order
        discount = min(offer_amount, order_total_without_offer)
        order_total = order_total_without_offer - discount

    ############################## Exception handling block #################################
    
    # Handle AssertionError
    except AssertionError as ae:
        message = ae.args[0]    # getting the message
        return JsonResponse(message, status=message["status code"])

    # Handle JSONDecodeError
    except JSONDecodeError:
        return JsonResponse(create_HTTP_error_message(400, "JSON payload is not valid. Check for correct syntax!"), status=400)

    # Handle TypeError
    except TypeError:
        return JsonResponse(create_HTTP_error_message(400, "wrong types included for values in the payload :("), status=400)

    # Handle LookupError
    except LookupError:
        return JsonResponse(create_HTTP_error_message(400, "something is missing in the payload!"), status=400)
    
    # Handle all other errors/exceptions
    except Exception as e:
        if len(e.args)>0 and isinstance(e.args[0], dict):
            err_msg = e.args[0]
            return JsonResponse(err_msg, status=err_msg["status code"])
        else:
            return JsonResponse(create_HTTP_error_message(500, e), status=500)

    # if no exceptions
    else:
        # return total order as JSON
        return JsonResponse({"order_total": order_total})