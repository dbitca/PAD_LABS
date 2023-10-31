from flask import Flask, jsonify, request
from expiringdict import ExpiringDict
import requests
import logging

app = Flask(__name__)

INGREDIENT_MICROSERVICE_URL = None
RECIPE_MICROSERVICE_URL = None

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
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

    # Execute fetch_microservice_urls function before the first request
@app.before_first_request
def before_first_request():
    fetch_microservice_urls()

def fetch_microservice_urls():
    global INGREDIENT_MICROSERVICE_URL, RECIPE_MICROSERVICE_URL

    service_discovery_url = "http://127.0.0.1:8001"


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
        service_url = f"http://127.0.0.1:{service_port}"

        return {"status": "online", "info": service_info, "url": service_url}
    else:
        return {"status": "offline", "info": {}, "url": None}

@app.route('/status', methods=['GET'])
def application_status():
    ingredient_response = requests.get(f"{INGREDIENT_MICROSERVICE_URL}/status")
    recipe_response = requests.get(f"{RECIPE_MICROSERVICE_URL}/status")

    ingredient_status = "Online" if ingredient_response.status_code == 200 else "Offline"
    recipe_status = "Online" if recipe_response.status_code == 200 else "Offline"

    status_info = {
        "Ingredient Microservice Status": ingredient_status,
        "Recipe Microservice Status": recipe_status
    }

    return jsonify(status_info)

#Controller to access the ingredient endpoints
@app.route('/ingredients', methods = ['GET'])

def get_ingredients():
    url = f"{INGREDIENT_MICROSERVICE_URL}/ingredients"
    response = requests.get(url)

    if response.status_code == 200:
        ingredients = response.json()
        return jsonify(ingredients)
    else:
        return jsonify({"error": "Failed to retrieve ingredients"}), response.status_code


@app.route('/ingredients', methods=['POST'])
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
def add_ingredients():
    url = f"{INGREDIENT_MICROSERVICE_URL}/addIngredients"
    request_data = request.get_json()

    response = requests.post(url, json=request_data)

    if response.status_code == 200:
        return jsonify({"message": "Ingredients added successfully!"})
    else:
        return jsonify({"error": "Failed to add ingredients"}), response.status_code

@app.route('/ingredient/<id>', methods=['GET'])
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

@app.route('/update', methods=['PUT'])
def update_ingredient():
    url = f"{INGREDIENT_MICROSERVICE_URL}/update"

    request_data = request.get_json()
    ingredient_entity = request_data.get("ingredient")

    response = requests.put(url, json={
        "ingredient" : ingredient_entity
    })

    return jsonify(response.json()), response.status_code

@app.route('/recipes', methods=['GET'])
def get_recipes():
    url = f"{RECIPE_MICROSERVICE_URL}/recipes"
    response = requests.get(url)

    if response.status_code == 200:
        recipes = response.json()
        return jsonify(recipes)
    else:
        return jsonify({"error": "Failed to retrieve recipes"}), response.status_code

@app.route('/recipes/<ingredient>', methods=['GET'])
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
def add_recipe():
    url = f"{RECIPE_MICROSERVICE_URL}/addRecipe"
    request_data = request.get_json()
    response = requests.post(url, json=request_data)
    print(f'Added recipe. Response:{response.json()}, Status code: {response.status_code}')

    return 'Recipe added successfully!'