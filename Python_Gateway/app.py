import circuitbreaker
from circuitbreaker import CircuitBreaker, CircuitBreakerError
from flask import Flask, jsonify, request, abort
from pycircuitbreaker import circuit
from expiringdict import ExpiringDict
import requests
import logging
import os
from CustomCircuitBreaker import CustomCircuitBreaker

app = Flask(__name__)

# circuit_breaker = CustomCircuitBreaker()

# INGREDIENT_MICROSERVICE_URL = None
# RECIPE_MICROSERVICE_URL = None

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

# INGREDIENT_MICROSERVICE_URL = 'http://192.168.0.91:9191'
# RECIPE_MICROSERVICE_URL = 'http://192.168.0.69:8081'
    # Execute fetch_microservice_urls function before the first request
@app.before_first_request
def before_first_request():
    fetch_microservice_urls()

def fetch_microservice_urls():
    global INGREDIENT_MICROSERVICE_URL, RECIPE_MICROSERVICE_URL

    service_discovery_url = "http://192.168.0.81:8001"


    ingredient_status = fetch_service_info("IngredientMicroservice", service_discovery_url)
    if ingredient_status.get("status") == "online":
        INGREDIENT_MICROSERVICE_URL = ingredient_status.get("url")

        recipe_status = fetch_service_info("RecipeMicroservice", service_discovery_url)
    if recipe_status.get("status") == "online":
        RECIPE_MICROSERVICE_URL = recipe_status.get("url")

        logger.info("Microservice URLs set")



def fetch_service_info(service_name, service_discovery_url):
    service_info_url = f"{service_discovery_url}/get_info/{service_name}"

    response = requests.get(service_info_url)
    if response.status_code == 200:
        service_info = response.json()
        logger.info(service_info)


        service_name = service_info['name']
        service_port = service_info['port']
        service_host = service_info['host']
        service_url = f"http://{service_host}:{service_port}"

        return {"status": "online", "info": service_info, "url": service_url}
    else:
        return {"status": "offline", "info": {}, "url": None}
@CustomCircuitBreaker()
@app.route('/status', methods=['GET'])
def application_status():
    try:
        ingredient_response = requests.get(f"{INGREDIENT_MICROSERVICE_URL}/status")
        recipe_response = requests.get(f"{RECIPE_MICROSERVICE_URL}/status")

        ingredient_status = "Online" if ingredient_response.status_code == 200 else "Offline"
        recipe_status = "Online" if recipe_response.status_code == 200 else "Offline"

        status_info = {
        "Ingredient Microservice Status": ingredient_status,
        "Recipe Microservice Status": recipe_status
        }
        return jsonify(status_info)
    except CircuitBreakerError as e:
        error_message = f"Circuit breaker active: {e}"
        abort(503, description=error_message)
    # except requests.RequestException as e:
    #     error_message = f"Failed to call external service"
    #     abort(500, description = error_message)

#Controller to access the ingredient endpoints
@app.route('/ingredients', methods = ['GET'])
# @circuit(breaker=CustomCircuitBreaker)
def get_ingredients():
    url = f"{INGREDIENT_MICROSERVICE_URL}/ingredients"
    response = requests.get(url)

    if response.status_code == 200:
        ingredients = response.json()
        return jsonify(ingredients)
    else:
        return jsonify({"error": "Failed to retrieve ingredients"}), response.status_code


@app.route('/ingredients', methods=['POST'])
# @circuit(breaker=CustomCircuitBreaker)
def add_ingredient():
    url = f"{INGREDIENT_MICROSERVICE_URL}/addIngredient"
    request_data = request.get_json()
    ingredient_name = request_data.get("ingredient")

    response = requests.post(url, json={
        "ingredient": ingredient_name
    })
    print(f'Added ingredient: {ingredient_name}. Response: {response.json()}, Status code: {response.status_code}')

    return 'Ingredients added successfully!'

@app.route('/add_ingredients', methods=['POST'])
# @circuit(breaker=CustomCircuitBreaker)
def add_ingredients():
    url = f"{INGREDIENT_MICROSERVICE_URL}/addIngredients"
    request_data = request.get_json()

    response = requests.post(url, json=request_data)

    if response.status_code == 200:
        return jsonify({"message": "Ingredients added successfully!"})
    else:
        return jsonify({"error": "Failed to add ingredients"}), response.status_code

@app.route('/ingredient/<id>', methods=['GET'])
# @circuit(breaker=CustomCircuitBreaker)
def get_ingredeint_by_id(id):
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

# @app.route('/update', methods=['PUT'])
# def update_ingredient():
#     url = f"{INGREDIENT_MICROSERVICE_URL}/update"
#
#     request_data = request.get_json()
#     ingredient_entity = request_data.get("ingredient")
#
#     response = requests.put(url, json={
#         "ingredient" : ingredient_entity
#     })
#
#     return jsonify(response.json()), response.status_code

@app.route('/recipes', methods=['GET'])
# @circuit(breaker=CustomCircuitBreaker)
def get_recipes():
    url = f"{RECIPE_MICROSERVICE_URL}/recipes"
    response = requests.get(url)

    if response.status_code == 200:
        recipes = response.json()
        return jsonify(recipes)
    else:
        return jsonify({"error": "Failed to retrieve recipes"}), response.status_code

@app.route('/recipes/<ingredient>', methods=['GET'])
# @circuit(breaker=CustomCircuitBreaker)
def get_recipe_by_ingredient(ingredient):
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

@app.route('/add_recipe', methods=['POST'])
# @circuit(breaker=CustomCircuitBreaker)
def add_recipe():
    url = f"{RECIPE_MICROSERVICE_URL}/addRecipe"
    request_data = request.get_json()
    response = requests.post(url, json=request_data)
    print(f'Added recipe. Response:{response.json()}, Status code: {response.status_code}')

    return 'Recipe added successfully!'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)