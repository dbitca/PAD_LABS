package com.example.recipemicroservice.rest;

import com.example.recipemicroservice.domain.Recipes;
import com.example.recipemicroservice.service.RecipeService;
import org.apache.coyote.Response;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.health.Health;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.MediaType;


import java.util.List;

@RestController
public class RecipeController {
   Recipes recipe = new Recipes();

    private final RecipeService recipeService;

    HealthIndicator healthIndicator = new HealthIndicator() {
        @Override
        public Health health() {
            return Health.up().build();
        }
    };

    @GetMapping("/status")
    public String getStatus(){
        Health health = healthIndicator.health();
        return "Service status: " + health.getStatus();
    }

    public RecipeController(RecipeService recipeService) {
        this.recipeService = recipeService;
    }

    @PostMapping("/notify")
    public String receiveNotification(@RequestBody String message){
        System.out.println("Received message" + message);
        return "Received message: " + message;
    }

    @PostMapping(value = "/addRecipe")
    public Recipes saveRecipe(@RequestBody Recipes recipe){
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
}


