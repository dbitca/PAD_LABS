package com.example.recipemicroservice.rest;

import com.example.recipemicroservice.domain.Recipes;
import com.example.recipemicroservice.service.RecipeService;
import org.apache.coyote.Response;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.health.Health;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.MediaType;


import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;


@RestController
public class RecipeController {
   Recipes recipe = new Recipes();

    private final RecipeService recipeService;

    @Autowired
    @Qualifier("taskExecutor")
    private ThreadPoolTaskExecutor taskExecutor;

    Logger logger = LoggerFactory.getLogger(RecipeController.class);

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
        logger.info("Received message" + message);
        return "Received message: " + message;
    }

    @PostMapping(value = "/addRecipe")
    public Recipes saveRecipe(@RequestBody Recipes recipe) {
        logger.info("Received a request to add a recipe. Thread: " + Thread.currentThread().getName());
        CompletableFuture<Recipes> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to save recipe. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return recipeService.saveRecipe(recipe);
        }, taskExecutor);

        try {
            Recipes result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return new Recipes();
        } catch (Exception e) {
            return new Recipes();
        }
    }
    @GetMapping("/recipe/{recipeId}")
    public Recipes findRecipeById(@PathVariable Long recipeId) {
        logger.info("Received a request to retrieve a recipe by ID. Thread: " + Thread.currentThread().getName());
        CompletableFuture<Recipes> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to retrieve a recipe by ID. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            Recipes result = recipeService.getRecipeById(recipeId);
            if (result == null) {
                throw new RuntimeException("Recipe not found");
            }
            return result;
        }, taskExecutor);

        try {
            Recipes result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return new Recipes();
        } catch (Exception e) {
            return new Recipes();
        }
    }

    @GetMapping("/recipes")
    public List<Recipes> findAllRecipes() {
        logger.info("Received a request to get all recipes. Thread: " + Thread.currentThread().getName());
        CompletableFuture<List<Recipes>> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to get recipes. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return recipeService.getRecipes();
        }, taskExecutor);

        try {
            List<Recipes> result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return Collections.emptyList();
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    @GetMapping("/recipes/{ingredient}")
    public List<Recipes> getRecipesByIngredient(@PathVariable String ingredient) {
        logger.info("Received a request to get recipes by ingredient. Thread: " + Thread.currentThread().getName());
        CompletableFuture<List<Recipes>> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to get recipes by ingredient. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return recipeService.findRecipesByIngredient(ingredient);
        }, taskExecutor);

        try {
            List<Recipes> result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return Collections.emptyList();
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }
}


