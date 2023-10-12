package com.example.ingredientmicroservice.service;

import com.example.ingredientmicroservice.domain.Ingredients;
import com.example.ingredientmicroservice.repository.IngredientRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

@Service
public class IngredientServiceImpl{
    private final IngredientRepository ingredientRepository;
    Logger logger = LoggerFactory.getLogger(IngredientServiceImpl.class);

    private <T> CompletableFuture<T> executeWithTimeout(Supplier<CompletableFuture<T>> taskSupplier, long timeoutInSeconds) {
        CompletableFuture<T> taskFuture = taskSupplier.get();
        return taskFuture.orTimeout(timeoutInSeconds, TimeUnit.SECONDS);
    }
    Object target;
    public IngredientServiceImpl(IngredientRepository ingredientRepository) {
        this.ingredientRepository = ingredientRepository;
    }

    public CompletableFuture<CompletableFuture<List<Ingredients>>> saveIngredients(MultipartFile file, long timeoutInSeconds) throws Exception {
        return executeWithTimeout(() -> {
            try {
                return CompletableFuture.completedFuture(parseAndSaveIngredients(file));
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }, timeoutInSeconds);
    }

    private CompletableFuture<List<Ingredients>> parseAndSaveIngredients(MultipartFile file) throws Exception {
        List<Ingredients> ingredients = parseCSVFile(file);
        logger.info("saving a list of ingredients of size {}", ingredients.size());
        ingredients = ingredientRepository.saveAll(ingredients);
        return CompletableFuture.completedFuture(ingredients);
    }


    public Ingredients saveIngredient(Ingredients ingredient){
       return ingredientRepository.save(ingredient);
    }


    public List<Ingredients> getIngredients(){
        return ingredientRepository.findAll();
    }

    public Ingredients getIngredientById(Long id){
        return ingredientRepository.findById(id).orElse(null);
    }

    public String deleteIngredient (Long id){
        ingredientRepository.deleteById(id);
        return "product removed " + id;
    }

    public Ingredients updateIngredient (Ingredients ingredient){
       Ingredients existingIngredient = ingredientRepository.findById((ingredient.getId())).orElse(null);
       existingIngredient.setIngredient(ingredient.getIngredient());
       return ingredientRepository.save(existingIngredient);
    }

    private List<Ingredients> parseCSVFile(final MultipartFile file) throws Exception {
        final List<Ingredients> ingredients = new ArrayList<>();
        try {
            try (final BufferedReader br = new BufferedReader(new InputStreamReader(file.getInputStream()))) {
                String line;
                while ((line = br.readLine()) != null) {
                    final String[] data = line.split(",");
                    final Ingredients ingredient = new Ingredients();
                    ingredient.setIngredient(data[0]);
                    ingredients.add(ingredient);
                }
                return ingredients;
            }
        } catch (final IOException e) {
            logger.error("Failed to parse CSV file {}", e);
            throw new Exception("Failed to parse CSV file {}", e);
        }
    }
}
