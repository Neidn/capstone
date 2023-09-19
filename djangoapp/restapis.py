import requests
import json
from .models import CarDealer, DealerReview, SENTIMENT
from requests.auth import HTTPBasicAuth
import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    status_code = 500

    # apikey from arg
    apikey = kwargs.get('apikey', None)
    password = kwargs.get('password', None)

    del kwargs['apikey']
    del kwargs['password']

    params = {}
    for key, value in kwargs.items():
        params[key] = value

    print("With params {}".format(params))
    try:
        # Call get method of requests library with URL and parameters
        if apikey:
            response = requests.get(url,
                                    headers={'Content-Type': 'application/json'},
                                    params=params,
                                    auth=HTTPBasicAuth(apikey, password)
                                    )

        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except Exception as err:
        # If any error occurs
        print("Network exception occurred")
        print("Error: {}".format(err))

        return {"error": "Network exception occurred"}, status_code


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    status_code = 500

    # apikey from arg
    apikey = kwargs.get('apikey', None)
    password = kwargs.get('password', None)

    del kwargs['apikey']
    del kwargs['password']

    params = {}
    for key, value in kwargs.items():
        params[key] = value

    print("With params {}".format(params))
    try:
        # Call get method of requests library with URL and parameters
        if apikey:
            response = requests.post(url,
                                     headers={'Content-Type': 'application/json'},
                                     params=params,
                                     auth=HTTPBasicAuth(apikey, password),
                                     json=payload
                                     )

        else:
            response = requests.post(url, headers={'Content-Type': 'application/json'},
                                     params=kwargs,
                                     json=payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except Exception as err:
        # If any error occurs
        print("Network exception occurred")
        print("Error: {}".format(err))

        return {"error": "Network exception occurred"}, status_code


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call post_request with a URL parameter
    json_result = get_request(
        url,
        include_docs=True,
        apikey=env('CLOUDANT_DEALERSHIPS_API_KEY'),
        password=env('CLOUDANT_DEALERSHIPS_PASSWORD')
    )

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]

            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results


# Create a get_dealer_id_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_by_id_from_cf(url, dealerId):
    results = []

    json_result = post_request(
        url,
        payload={
            "selector": {
                "_id": {
                    "$gt": "0"
                },
                "id": {
                    "$eq": 10
                }
            },
        },
        apikey=env('CLOUDANT_DEALERSHIPS_API_KEY'),
        password=env('CLOUDANT_DEALERSHIPS_PASSWORD'),
        include_docs=True,
    )

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["docs"]
        # For each dealer object
        for dealer_doc in dealers:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results[0] if results else None


# def get_dealer_reviews_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = post_request(
        url,
        apikey=env('CLOUDANT_REVIEWS_API_KEY'),
        password=env('CLOUDANT_REVIEWS_PASSWORD'),
        include_docs=True,
        payload={
            "selector": {
                "_id": {
                    "$gt": 0
                },
                "dealership": {
                    "$eq": int(dealerId)
                }
            },
        }

    )

    print(json_result)

    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["docs"]
        # For each dealer object
        for review_doc in reviews:
            # Create a CarDealer object with values in `doc` object

            sentiment = analyze_review_sentiments(review_doc["review"])

            print(f"Review First: {review_doc['review']} {sentiment}")

            review_obj = DealerReview(
                dealership=review_doc["dealership"],
                name=review_doc["name"],
                purchase=review_doc["purchase"],
                purchase_date=review_doc["purchase_date"] if review_doc["purchase"] else None,
                review=review_doc["review"],
                id=review_doc["id"],
                car_make=review_doc["car_make"] if review_doc["purchase"] else None,
                car_model=review_doc["car_model"] if review_doc["purchase"] else None,
                car_year=review_doc["car_year"] if review_doc["purchase"] else None,
                sentiment=sentiment,
            )
            results.append(review_obj)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    params = json.dumps(
        {
            "text": text,
            "features":
                {
                    "sentiment": {}
                }
        }
    )

    result = 'neutral'

    response = requests.post(
        env('NLU_API_URL'),
        data=params,
        headers={'Content-Type': 'application/json'},
        auth=HTTPBasicAuth('apikey', env('NLU_API_KEY'))
    )

    try:
        result = response.json()['sentiment']['document']['label']
        return result
    except KeyError:
        return result
