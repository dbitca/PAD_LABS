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

}
