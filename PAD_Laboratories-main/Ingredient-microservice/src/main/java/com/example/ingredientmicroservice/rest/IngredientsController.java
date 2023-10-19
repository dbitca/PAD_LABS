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
import java.util.List;
import java.util.concurrent.CompletableFuture;

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

    @PostMapping("/addIngredient")
    public Ingredients addIngredient(@RequestBody Ingredients ingredientEntity){
//        String message = "Ingredient " + ingredientEntity.getIngredient() + " is now available for use.";
//        restTemplate.postForObject("http://localhost:8081/notify", message, String.class);
        return ingredientsService.saveIngredient(ingredientEntity);
    }

    @Autowired
    @Qualifier("taskExecutor")
    private ThreadPoolTaskExecutor taskExecutor;

    @PostMapping("/addIngredients")
    public List<Ingredients> addIngredients(@RequestBody List<Ingredients> ingredientEntities) {
        return ingredientsService.saveIngredients(ingredientEntities);
    }

//    @PostMapping(value = "/addIngredients", consumes = {MediaType.MULTIPART_FORM_DATA_VALUE}, produces = "application" +
//            "/json")
//    public ResponseEntity addIngredients(@RequestParam(value = "files") MultipartFile[] files) throws Exception {
//        List<CompletableFuture<Void>> futures = new ArrayList<>();

//        for (MultipartFile file : files) {
//            CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
//                try {
//
//                    long threadId = Thread.currentThread().getId();
//                    String threadName = Thread.currentThread().getName();
//
//                    logger.info("Processing started for file: {} on thread ID: {} (Thread Name: {})",
//                            file.getOriginalFilename(), threadId, threadName);
//
//                    ingredientsService.saveIngredients(file, 1);
//
//                    logger.info("Processing completed for file: {} on thread ID: {} (Thread Name: {})",
//                            file.getOriginalFilename(), threadId, threadName);
//                } catch (Exception e) {
//                    logger.error("Error processing file: " + file.getOriginalFilename() + " on thread ID: " + Thread.currentThread().getId() + " (Thread Name: " + Thread.currentThread().getName() + ")", e);
//                }
//            }, taskExecutor);
//
//            futures.add(future);
//        }
//
//        CompletableFuture<Void>[] futuresArray = futures.toArray(new CompletableFuture[0]);
//        CompletableFuture<Void> allOf = CompletableFuture.allOf(futuresArray);
//        allOf.join();
//
//        return ResponseEntity.status(HttpStatus.CREATED).build();
//    }

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


