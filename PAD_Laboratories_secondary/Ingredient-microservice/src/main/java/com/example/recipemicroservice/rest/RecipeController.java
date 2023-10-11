package com.example.recipemicroservice.rest;

import com.example.recipemicroservice.domain.Recipes;
import com.example.recipemicroservice.service.RecipeService;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@RestController
public class RecipeController {
   Recipes recipe = new Recipes();

    private final RecipeService recipeService;

    public RecipeController(RecipeService recipeService) {
        this.recipeService = recipeService;
    }

    @PostMapping("/notify")
    public String receiveNotification(@RequestBody String message){
        System.out.println("Received message" + message);
        return "Received message: " + message;
    }

    @PostMapping("/addRecipe")
    public Recipes saveRecipe (@RequestBody Recipes recipe){
        return recipeService.saveRecipe(recipe);
    }

    @GetMapping("/recipe/{recipeId}")
    public Recipes findRecipeById(@PathVariable Long recipeId){
        return recipeService.getRecipeById(recipeId);
    }
    @GetMapping("/recipes")
    public List<Recipes> findAllRecipes(){
        return recipeService.getRecipes();
    }

    @GetMapping("/recipes/{ingredient}")
    public List<Recipes> getRecipesByIngredient(@PathVariable String ingredient){
        return recipeService.findRecipesByIngredient(ingredient);
    }

//    @GetMapping("/ingredient/{id}")
//    public Recipes findIngredientById(@PathVariable Long id){
//        String url = "http://localhost:9191/ingredient/" + id;
//        return restTemplate.getForObject(url, Recipes.class);
//    }

//

//    public IngredientsController(IngredientServiceImpl ingredientsService) {
//        this.ingredientsService = ingredientsService;
//    }
//

//
//    @PostMapping("/addIngredients")
//    public List<Ingredients> addIngredients(@RequestBody List<Ingredients> ingredientEntities){
//        return ingredientsService.saveIngredients(ingredientEntities);
//    }
//

//    @GetMapping("/ingredient/{id}")
//    public Ingredients findIngredientById(@PathVariable Long id){
//        return ingredientsService.getIngredientById(id);
//    }
//
//    @PutMapping("/update")
//    public Ingredients updateIngredient(@RequestBody Ingredients ingredientEntity){
//        return ingredientsService.updateIngredient(ingredientEntity);
//    }
//
//    @DeleteMapping("/delete/{id}")
//    public String deleteIngredient(@PathVariable Long id){
//        return ingredientsService.deleteIngredient(id);
//    }
}


