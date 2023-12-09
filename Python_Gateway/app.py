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
RECIPE_MICROSERVICE_URL1 = os.environ.get('RECIPE_MICROSERVICE_URL')
# RECIPE_MICROSERVICE_URL1 = os.environ.get('RECIPE_MICROSERVICE_URL1')
# RECIPE_MICROSERVICE_URL2 = os.environ.get('RECIPE_MICROSERVICE_URL2')


# print(f"Recipe 1 URL {RECIPE_MICROSERVICE_URL1}")
# print(f"Recipe 2 URL {RECIPE_MICROSERVICE_URL2}")

INGREDIENT_MICROSERVICE_URL = [
    INGREDIENT_MICROSERVICE_URL1,
    INGREDIENT_MICROSERVICE_URL2
]

RECIPE_MICROSERVICE_URL = [
    RECIPE_MICROSERVICE_URL1
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
        if isinstance(exception, (requests.exceptions.RequestException, NoHealthyServiceError)):
            print(f"Error occurred: {exception}")

        if hasattr(exception, 'response') and exception.response is not None:
            return 500 <= exception.response.status_code < 600

        print(f"Reroutes: {list(self.reroutes)}")
        print(f"Last Tripped: {self.last_tripped}")
        return (
            isinstance(exception, (requests.exceptions.RequestException, NoHealthyServiceError))
            and ((len(self.reroutes) >= self.threshold
            and time.time() - self.reroutes[0] <= self.timeout)
            or len(self.reroutes) >= 3
        )
    )
class CircuitBreakerOpenError(Exception):
    pass

class NoHealthyServiceError(Exception):
    pass
class LoadBalancer:
    def __init__(self, services):
        self.services = services
        self.current_index = 0

    def get_next_service(self):
        initial_index = self.current_index
        attempts = 0

        while attempts < len(self.services):
            service = self.services[self.current_index]
            try:
                response = requests.get(f"{service}/status")

                if response.status_code == 200:
                    return service
            except requests.exceptions.RequestException as e:
            # Log or handle the exception if needed
                pass

            self.current_index = (self.current_index + 1) % len(self.services)
            attempts += 1

        # Reset current_index to the initial value
        self.current_index = initial_index
        raise NoHealthyServiceError("No healthy services available")

circuit_breaker = CircuitBreaker(threshold=2, timeout=30)

ingredient_load_balancer = LoadBalancer(INGREDIENT_MICROSERVICE_URL)
recipe_load_balancer = LoadBalancer(RECIPE_MICROSERVICE_URL)

@app.route('/status', methods=['GET'])
@circuit_breaker
def application_status():
    try:
        ingredient_microservice_url = ingredient_load_balancer.get_next_service()
        recipe_microservice_url = recipe_load_balancer.get_next_service()

        logger.info(f"Request sent to Ingredient Microservice with URL:{ingredient_microservice_url}")
        logger.info(f"Request sent to Recipe Microservice with URL:{recipe_microservice_url}")

        ingredient_response=requests.get(f"{ingredient_microservice_url}/status")
        recipe_response = requests.get(f"{recipe_microservice_url}/status")

        ingredient_status = "Online" if ingredient_response.status_code == 200 else "Offline"
        recipe_status = "Online" if recipe_response.status_code == 200 else "Offline"

        status_info = {
        "Ingredient Microservice Status": ingredient_status,
        "Recipe Microservice Status": recipe_status
        }
        return jsonify(status_info)
    except NoHealthyServiceError:
        if circuit_breaker.should_trip(NoHealthyServiceError):
            circuit_breaker.trip()
        raise
    except Exception as e:
        if circuit_breaker.should_trip(e):
            circuit_breaker.trip()
        # raise e
        return(f"Exception occurred: {type(e).__name__}: {e}")

@app.route('/ingredients', methods = ['GET'])
@circuit_breaker
def get_ingredients():
    try:
        ingredient_microservice_url = ingredient_load_balancer.get_next_service()
        url = f"{ingredient_microservice_url}/ingredients"

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
        ingredient_microservice_url = ingredient_load_balancer.get_next_service()
        url = f"{ingredient_microservice_url}/addIngredient"

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
        ingredient_microservice_url = ingredient_load_balancer.get_next_service()
        url = f"{ingredient_microservice_url}/addIngredients"

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
            recipe_microservice_url = recipe_load_balancer.get_next_service()
            url = f"{recipe_microservice_url}/ingredient/{id}"

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
        recipe_microservice_url = recipe_load_balancer.get_next_service()
        url = f"{recipe_microservice_url}/recipes"

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
            recipe_microservice_url = recipe_load_balancer.get_next_service()
            url = f"{recipe_microservice_url}/recipes/{ingredient}"
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
        recipe_microservice_url = recipe_load_balancer.get_next_service()
        url = f"{recipe_microservice_url}/addRecipe"

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