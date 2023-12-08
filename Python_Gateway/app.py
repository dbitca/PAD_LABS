from flask import Flask, jsonify, request, abort
from expiringdict import ExpiringDict
import requests
import logging
import os
from collections import deque
import functools
import time

app = Flask(__name__)

# circuit_breaker = CustomCircuitBreaker()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to the console
        # logging.FileHandler('my_log.log')  # Log to a file
    ]
)

logger = logging.getLogger(__name__)

#ExipringDict instance for ingredients
ingredient_cache = ExpiringDict(max_len=50, max_age_seconds=600, items=None)

#ExpiringDict instance for recipes
recipe_cache = ExpiringDict(max_len=50, max_age_seconds=600, items=None)

@app.route('/')
def home():
    return 'API Gateway Home'

global INGREDIENT_MICROSERVICE_URL1, INGREDIENT_MICROSERVICE_URL2, RECIPE_MICROSERVICE_URL
INGREDIENT_MICROSERVICE_URL1 = os.environ.get('INGREDIENT_MICROSERVICE_URL1')
INGREDIENT_MICROSERVICE_URL2 = os.environ.get('INGREDIENT_MICROSERVICE_URL2')
RECIPE_MICROSERVICE_URL = os.environ.get('RECIPE_MICROSERVICE_URL')


print(f"Ingredient 1 URL {INGREDIENT_MICROSERVICE_URL1}")
print(f"Ingredient 2 URL {INGREDIENT_MICROSERVICE_URL2}")

MICROSERVICE_URL = [
    INGREDIENT_MICROSERVICE_URL1,
    INGREDIENT_MICROSERVICE_URL2
]

class CircuitBreaker:
    def __init__(self, threshold, timeout):
        self.threshold = threshold
        self.timeout = timeout
        self.reroutes = deque(maxlen=threshold)
        self.last_tripped = None

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if self.is_open:
                    logger.info("CircuitBreaker is now open")
                    raise CircuitBreakerOpenError("Circuit breaker is open")
                self.reroutes.append(time.time())
                return func(*args, **kwargs)
            except Exception as e:
                if self.should_trip(e):
                    self.trip()
                raise e
        return wrapper

    @property
    def is_open(self):
        return self.last_tripped and time.time() - self.last_tripped < self.timeout

    def trip(self):
        self.last_tripped = time.time()

    def should_trip(self, exception):
        if isinstance(exception, requests.exceptions.ConnectionError):
            print(f"ConnectionError occurred: {exception}")
        print(f"Reroutes: {list(self.reroutes)}")
        print(f"Last Tripped: {self.last_tripped}")
        return (
            isinstance(exception, requests.exceptions.ConnectionError)
            and ((len(self.reroutes) >= self.threshold
            and time.time() - self.reroutes[0] <= self.timeout)
            or len(self.reroutes) >= 3
        )
    )
class CircuitBreakerOpenError(Exception):
    pass

class RoundRobinLoadBalancer:
    def __init__(self, services):
        self.services = services
        self.current_index = 0

    def get_next_service(self):
        service = self.services[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.services)
        return service

# @app.before_first_request
# def before_first_request():
#     fetch_microservice_urls()

# def fetch_microservice_urls():
#     global INGREDIENT_MICROSERVICE_URL, RECIPE_MICROSERVICE_URL
#
#     service_discovery_url = "http://192.168.0.81:8001"
#
#     ingredient_status = fetch_service_info("IngredientMicroservice", service_discovery_url)
#     if ingredient_status.get("status") == "online":
#         INGREDIENT_MICROSERVICE_URL = ingredient_status.get("url")
#
#         recipe_status = fetch_service_info("RecipeMicroservice", service_discovery_url)
#     if recipe_status.get("status") == "online":
#         RECIPE_MICROSERVICE_URL = recipe_status.get("url")
#
#         logger.info("Microservice URLs set")
#
# def fetch_service_info(service_name, service_discovery_url):
#     service_info_url = f"{service_discovery_url}/get_info/{service_name}"
#
#     response = requests.get(service_info_url)
#     if response.status_code == 200:
#         service_info = response.json()
#         logger.info(service_info)
#
#
#         service_name = service_info['name']
#         service_port = service_info['port']
#         service_host = service_info['host']
#         service_url = f"http://{service_host}:{service_port}"
#
#         return {"status": "online", "info": service_info, "url": service_url}
#     else:
#         return {"status": "offline", "info": {}, "url": None}

circuit_breaker = CircuitBreaker(threshold=2, timeout=30)

load_balancer = RoundRobinLoadBalancer(MICROSERVICE_URL)

@app.route('/status', methods=['GET'])
@circuit_breaker
def application_status():
    try:

        ingredient_response1 = requests.get(f"{INGREDIENT_MICROSERVICE_URL1}/status")
        ingredient_response2 = requests.get(f"{INGREDIENT_MICROSERVICE_URL2}/status")
        recipe_response = requests.get(f"{RECIPE_MICROSERVICE_URL}/status")

        ingredient_status1 = "Online" if ingredient_response1.status_code == 200 else "Offline"
        ingredient_status2 = "Online" if ingredient_response2.status_code == 200 else "Offline"
        recipe_status = "Online" if recipe_response.status_code == 200 else "Offline"

        status_info = {
        "Ingredient Microservice 1 Status": ingredient_status1,
        "Ingredient Microservice 2 Status": ingredient_status2,
        "Recipe Microservice Status": recipe_status
        }
        return jsonify(status_info)
    except Exception as e:

        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        # raise e
        return(f"Exception occurred: {type(e).__name__}: {e}")

@app.route('/ingredients', methods = ['GET'])
@circuit_breaker
def get_ingredients():
    try:
        url = f"{INGREDIENT_MICROSERVICE_URL}/ingredients"
        response = requests.get(url)

        if response.status_code == 200:
            ingredients = response.json()
            return jsonify(ingredients)
        else:
            return jsonify({"error": "Failed to retrieve ingredients"}), response.status_code
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

@app.route('/ingredients', methods=['POST'])
@circuit_breaker
def add_ingredient():
    try:
        url = f"{INGREDIENT_MICROSERVICE_URL}/addIngredient"
        request_data = request.get_json()
        ingredient_name = request_data.get("ingredient")

        response = requests.post(url, json={
            "ingredient": ingredient_name
        })
        print(f'Added ingredient: {ingredient_name}. Response: {response.json()}, Status code: {response.status_code}')

        return 'Ingredients added successfully!'
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

@app.route('/add_ingredients', methods=['POST'])
@circuit_breaker
def add_ingredients():
    try:
        url = f"{INGREDIENT_MICROSERVICE_URL}/addIngredients"
        request_data = request.get_json()

        response = requests.post(url, json=request_data)

        if response.status_code == 200:
            return jsonify({"message": "Ingredients added successfully!"})
        else:
            return jsonify({"error": "Failed to add ingredients"}), response.status_code
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

@app.route('/ingredient/<id>', methods=['GET'])
@circuit_breaker
def get_ingredeint_by_id(id):
    try:
        cache_key = f'ingredient_{id}'
        cached_data = ingredient_cache.get(cache_key)
        if cached_data:
            print(f"Data taken from cache: {cached_data}")
            return jsonify(cached_data)
        else:
            url = f"{INGREDIENT_MICROSERVICE_URL}/ingredient/{id}"
            response = requests.get(url)

            if response.status_code == 200:
                ingredient = response.json()
                ingredient_cache[cache_key] = ingredient
                print("ingredient cache:", ingredient_cache)
                return jsonify(ingredient), response.status_code
            else:
                return jsonify({"error": "Failed to retrieve ingredient"}), response.status_code
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e
@app.route('/recipes', methods=['GET'])
@circuit_breaker
def get_recipes():
    try:
        url = f"{RECIPE_MICROSERVICE_URL}/recipes"
        response = requests.get(url)

        if response.status_code == 200:
            recipes = response.json()
            return jsonify(recipes)
        else:
            return jsonify({"error": "Failed to retrieve recipes"}), response.status_code
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

@app.route('/recipes/<ingredient>', methods=['GET'])
@circuit_breaker
def get_recipe_by_ingredient(ingredient):
    try:
        cache_key = f'recipe{ingredient}'
        cached_data = recipe_cache.get(cache_key)

        if cached_data:
            print(f"Data taken from cache: {cached_data}")
            return jsonify(cached_data)
        else:
            url = f"{RECIPE_MICROSERVICE_URL}/recipes/{ingredient}"
            response = requests.get(url)

            if response.status_code == 200:
                recipe=response.json()
                recipe_cache[cache_key] = recipe
                return jsonify(recipe)
            else:
                return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

@app.route('/add_recipe', methods=['POST'])
@circuit_breaker
def add_recipe():
    try:
        url = f"{RECIPE_MICROSERVICE_URL}/addRecipe"
        request_data = request.get_json()
        response = requests.post(url, json=request_data)
        print(f'Added recipe. Response:{response.json()}, Status code: {response.status_code}')

        return 'Recipe added successfully!'
    except Exception as e:
        print(f"Exception occurred: {type(e).__name__}: {e}")
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        raise e

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')