package com.example.recipemicroservice.service;

import com.example.recipemicroservice.domain.Recipes;
import com.example.recipemicroservice.repository.RecipeRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RecipeService {
    private final RecipeRepository recipeRepository;

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
