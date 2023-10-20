from flask import Flask, jsonify, request
from expiringdict import ExpiringDict
import requests

app = Flask(__name__)

INGREDEINT_MICROSERVICE_URL = "http://localhost:9191"
RECIPE_MICROSERVICE_URL = "http://localhost:8081"

#ExipringDict instance for ingredients
ingredient_cache = ExpiringDict(max_len=50, max_age_seconds=600, items=None)

#ExpiringDict instance for recipes
recipe_cache = ExpiringDict(max_len=50, max_age_seconds=600, items=None)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)

#Status endpoint
@app.route('/status', methods=['GET'])
def gateway_status():
    status = {"gateway": "online", "microservices": {}}

    ingredient_status = check_microservice_status(INGREDEINT_MICROSERVICE_URL)
    status["microservices"]["ingredient_microservice"] = ingredient_status

    recipe_status = check_microservice_status(RECIPE_MICROSERVICE_URL)
    status["microservices"]["recipe_microservice"] = recipe_status

    return jsonify(status)



#Controller to access the ingredient endpoints
@app.route('/ingredients', methods = ['GET'])

def get_ingredients():
    url = f"{INGREDEINT_MICROSERVICE_URL}/ingredients"
    response = requests.get(url)

    if response.status_code == 200:
        ingredients = response.json()
        return jsonify(ingredients)
    else:
        return jsonify({"error": "Failed to retrieve ingredients"}), response.status_code

@app.route('/add_ingredients', methods=['POST'])
def add_ingredient():
    url = f"{INGREDEINT_MICROSERVICE_URL}/addIngredient"
    request_data = request.get_json()
    ingredient_name = request_data.get("ingredient")

    response = requests.post(url, json={
        "ingredient": ingredient_name
    })
    print(f'Added ingredient: {ingredient_name}. Response: {response.json()}, Status code: {response.status_code}')

    return 'Ingredients added successfully!'

@app.route('/ingredient/<id>', methods=['GET'])
def get_ingredeint_by_id(id):
    cache_key = f'ingredient_{id}'
    cached_data = ingredient_cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)
    else:
        url = f"{INGREDEINT_MICROSERVICE_URL}/ingredient/{id}"
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
    url = f"{INGREDEINT_MICROSERVICE_URL}/update"

    request_data = request.get_json()
    ingredient_entity = request_data.get("ingredient")

    response = requests.put(url, json={
        "ingredient" : ingredient_entity
    })

    return jsonify(response.json()), response.status_code

#Controller to access the recipe endpoints
@app.route('/recipes', methods=['GET'])
def get_recipes():
    url = f"{RECIPE_MICROSERVICE_URL}/recipes"
    response = requests.get(url)

    if response.status_code == 200:
        recipes = response.json()
        return jsonify(recipes)
    else:
        return json({"error": "Failed to retrieve recipes"}), response.status_code

@app.route('/recipes/<ingredient>', methods=['GET'])
def get_recipe_by_ingredient(ingredient):
    cache_key = f'recipe{ingredient}'
    cached_data = recipe_cache.get(cache_key)

    if cached_data:
        print(recipe_cache)
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