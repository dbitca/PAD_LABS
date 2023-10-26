package com.example.ingredientmicroservice.rest;

import com.example.ingredientmicroservice.service.IngredientServiceImpl;
import com.example.ingredientmicroservice.domain.Ingredients;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.boot.actuate.health.Health;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import java.awt.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

@RestController
public class IngredientsController {
    RestTemplate restTemplate = new RestTemplate();
    Logger logger = LoggerFactory.getLogger(IngredientsController.class);

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

    @Autowired
    @Qualifier("taskExecutor")
    private ThreadPoolTaskExecutor taskExecutor;

    @PostMapping("/addIngredient")
    public Ingredients addIngredient(@RequestBody Ingredients ingredientEntity) {
        logger.info("Received a request to add an ingredient. Thread: " + Thread.currentThread().getName());
        CompletableFuture<Ingredients> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to save ingredient. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return ingredientsService.saveIngredient(ingredientEntity);
        }, taskExecutor);

        try {
            Ingredients result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return new Ingredients();
        } catch (Exception e) {
            return new Ingredients();
        }
    }

    @PostMapping("/addIngredients")
    public List<Ingredients> addIngredients(@RequestBody List<Ingredients> ingredientEntities) {
        logger.info("Received a request to add ingredients. Thread: " + Thread.currentThread().getName());
        CompletableFuture<List<Ingredients>> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to save ingredients. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(10000);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            return ingredientsService.saveIngredients(ingredientEntities);
        }, taskExecutor);

        try {
            List<Ingredients> result = future.get(5, TimeUnit.SECONDS);
            return result;
        } catch (TimeoutException e) {
            return Collections.emptyList();
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

 @GetMapping("/ingredients")
    public List<Ingredients> findAllIngredients(){  logger.info("Received a request to get all ingredients. Thread: " + Thread.currentThread().getName());
     CompletableFuture<List<Ingredients>> future = CompletableFuture.supplyAsync(() -> {
         logger.info("Starting asynchronous task to get ingredients. Thread: " + Thread.currentThread().getName());
         try {
             Thread.sleep(0);
         } catch (InterruptedException e) {
             throw new RuntimeException(e);
         }
         return ingredientsService.getIngredients();
     }, taskExecutor);

     try {
         List<Ingredients> result = future.get(1, TimeUnit.SECONDS); // Specify the timeout
         return result;
     } catch (TimeoutException e) {
         return Collections.emptyList();
     } catch (Exception e) {
         return Collections.emptyList();
     }

 }

    @GetMapping("/ingredient/{id}")
    public Ingredients findIngredientById(@PathVariable Long id) {
        logger.info("Received a request to retrieve ingredient by ID. Thread: " + Thread.currentThread().getName());
        CompletableFuture<Ingredients> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to retrieve ingredient by ID. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            Ingredients result = ingredientsService.getIngredientById(id);
            if (result == null) {
                throw new RuntimeException("Ingredient not found"); // Simulate a not found scenario
            }
            return result;
        }, taskExecutor);

        try {
            Ingredients result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return new Ingredients();
        } catch (Exception e) {
            return new Ingredients();
        }
    }

    @PutMapping("/update")
    public Ingredients updateIngredient(@RequestBody Ingredients ingredientEntity) {
        logger.info("Received a request to update ingredient. Thread: " + Thread.currentThread().getName());
        CompletableFuture<Ingredients> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to update ingredient. Thread: " + Thread.currentThread().getName());
            try {
                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            Ingredients result = ingredientsService.updateIngredient(ingredientEntity);
            if (result == null) {
                throw new RuntimeException("Ingredient not found");
            }
            return result;
        }, taskExecutor);

        try {
            Ingredients result = future.get(5, TimeUnit.SECONDS); // Specify the timeout
            return result;
        } catch (TimeoutException e) {
            return new Ingredients();
        } catch (Exception e) {
            return new Ingredients();
        }
    }

    @DeleteMapping("/delete/{id}")
    public String deleteIngredient(@PathVariable Long id) {
        logger.info("Received a request to delete ingredient. Thread: " + Thread.currentThread().getName());
        CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
            logger.info("Starting asynchronous task to delete ingredient. Thread: " + Thread.currentThread().getName());
            try {

                Thread.sleep(0);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
            String result = ingredientsService.deleteIngredient(id);
            if (result == null) {
                throw new RuntimeException("Ingredient not found");
            }
            return result;
        }, taskExecutor);

        try {
            String result = future.get(5, TimeUnit.SECONDS);
            return result;
        } catch (TimeoutException e) {
            return "Timeout occurred while deleting the ingredient";
        } catch (Exception e) {
            return "An error occurred while deleting the ingredient";
        }
    }
}


