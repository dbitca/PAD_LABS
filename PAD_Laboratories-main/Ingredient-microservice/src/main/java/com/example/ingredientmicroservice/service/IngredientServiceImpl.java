package com.example.ingredientmicroservice.service;

import com.example.ingredientmicroservice.domain.Ingredients;
import com.example.ingredientmicroservice.repository.IngredientRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class IngredientServiceImpl{
    private final IngredientRepository ingredientRepository;

    public IngredientServiceImpl(IngredientRepository ingredientRepository) {
        this.ingredientRepository = ingredientRepository;
    }

    public Ingredients saveIngredient(Ingredients ingredient){
       return ingredientRepository.save(ingredient);
    }

    public List<Ingredients> saveIngredients(List<Ingredients> ingredients){
        return ingredientRepository.saveAll(ingredients);
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
}
