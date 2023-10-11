package com.example.ingredientmicroservice.rest;

import com.example.ingredientmicroservice.service.IngredientServiceImpl;
import com.example.ingredientmicroservice.domain.Ingredients;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.health.Health;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.awt.*;
import java.util.List;

@RestController
public class IngredientsController {
    RestTemplate restTemplate = new RestTemplate();
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

    @PostMapping(value = "/addIngredients", consumes = {MediaType.MULTIPART_FORM_DATA_VALUE}, produces = "application" +
            "/json")
    public ResponseEntity addIngredients(@RequestParam(value = "files") MultipartFile[] files) throws Exception {
        for(MultipartFile file:files){
            ingredientsService.saveIngredients(file);
        }
        return ResponseEntity.status(HttpStatus.CREATED).build();
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


