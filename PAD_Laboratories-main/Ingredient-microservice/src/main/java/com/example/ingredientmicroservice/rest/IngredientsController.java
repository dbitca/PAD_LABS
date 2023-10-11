package com.example.ingredientmicroservice.rest;

import com.example.ingredientmicroservice.service.IngredientServiceImpl;
import com.example.ingredientmicroservice.domain.Ingredients;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@RestController
public class IngredientsController {
    RestTemplate restTemplate = new RestTemplate();

    @Value("${http://localhost:8081}")
    private String recipeServiceBaseUrl;

    private final IngredientServiceImpl ingredientsService;

    public IngredientsController(IngredientServiceImpl ingredientsService) {
        this.ingredientsService = ingredientsService;
    }

    @PostMapping("/addIngredient")
    public Ingredients addIngredient(@RequestBody Ingredients ingredientEntity){
        String message = "Ingredient " + ingredientEntity.getIngredient() + " is now available for use.";
        restTemplate.postForObject("http://localhost:8081/notify", message, String.class);
        return ingredientsService.saveIngredient(ingredientEntity);
    }

    @PostMapping("/addIngredients")
    public List<Ingredients> addIngredients(@RequestBody List<Ingredients> ingredientEntities){
        return ingredientsService.saveIngredients(ingredientEntities);
    }

    @GetMapping("/ingredients")
    public List<Ingredients> findAllIngredients(){
        return ingredientsService.getIngredients();
    }
    @GetMapping("/ingredient/{id}")
    public Ingredients findIngredientById(@PathVariable Long id){
        return ingredientsService.getIngredientById(id);
    }

    @PutMapping("/update")
    public Ingredients updateIngredient(@RequestBody Ingredients ingredientEntity){
        return ingredientsService.updateIngredient(ingredientEntity);
    }

    @DeleteMapping("/delete/{id}")
    public String deleteIngredient(@PathVariable Long id){
        return ingredientsService.deleteIngredient(id);
    }
}


