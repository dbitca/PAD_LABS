package com.example.recipemicroservice.service;

import com.example.recipemicroservice.domain.Recipes;
import com.example.recipemicroservice.repository.RecipeRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Service
public class RecipeService {
    private final RecipeRepository recipeRepository;

    Logger logger = LoggerFactory.getLogger(RecipeService.class);
    public RecipeService(RecipeRepository recipeRepository) {
        this.recipeRepository = recipeRepository;
    }

    public CompletableFuture<List<Recipes>> saveRecipes(MultipartFile file) throws Exception{
        long start = System.currentTimeMillis();
        List<Recipes> recipes = parseCSVFile(file);
        logger.info("saving a list of recipes of size {}", recipes.size(), "" + Thread.currentThread().getName());
        recipes = recipeRepository.saveAll(recipes);
        long end = System.currentTimeMillis();
        logger.info("Total time{}", (end - start));
        return CompletableFuture.completedFuture(recipes);
    }

    public Recipes saveRecipe (Recipes recipe){
       return recipeRepository.save(recipe);
    }

        public Recipes getRecipeById(Long id){
        return recipeRepository.findById(id).orElse(null);
    }

        public List<Recipes> getRecipes(){
        return recipeRepository.findAll();
    }

    public List<Recipes> findRecipesByIngredient(String ingredient) {
        return recipeRepository.findByIngredientsContaining(ingredient);
    }

    private List<Recipes> parseCSVFile(final MultipartFile file) throws Exception {
        final List<Recipes> recipes = new ArrayList<>();
        try {
            try (final BufferedReader br = new BufferedReader(new InputStreamReader(file.getInputStream()))) {
                String line;
                while ((line = br.readLine()) != null) {
                    final String[] data = line.split(",");
                    final Recipes recipe = new Recipes();
                    recipe.setRecipeId(data[0]);
                    recipe.setName(data[1]);
                    if (!data[2].isEmpty()) {
                        recipe.setIngredients(Arrays.asList(data[2].split(",")));
                    } else {
                        recipe.setIngredients(new ArrayList<>());
                    }
                    recipe.setInstructions(data[3]);
                    recipes.add(recipe);
                }
                return recipes;
            }
        } catch (final IOException e) {
            logger.error("Failed to parse CSV file {}", e);
            throw new Exception("Failed to parse CSV file {}", e);
        }
    }

}
