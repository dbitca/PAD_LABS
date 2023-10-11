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

@Service
public class IngredientServiceImpl{
    private final IngredientRepository ingredientRepository;
    Logger logger = LoggerFactory.getLogger(IngredientServiceImpl.class);

    Object target;
    public IngredientServiceImpl(IngredientRepository ingredientRepository) {
        this.ingredientRepository = ingredientRepository;
    }

   public CompletableFuture<List<Ingredients>> saveIngredients(MultipartFile file) throws Exception {
        long start = System.currentTimeMillis();
        List<Ingredients> ingredients = parseCSVFile(file);
        logger.info("saving a list of ingredients of size{}", ingredients.size(), "", Thread.currentThread().getId());
        ingredients = ingredientRepository.saveAll(ingredients);
        long end = System.currentTimeMillis();
        logger.info("Total time {}", (end-start));
        return CompletableFuture.completedFuture(ingredients);
   }

    public Ingredients saveIngredient(Ingredients ingredient){
       return ingredientRepository.save(ingredient);
    }

//    public List<Ingredients> saveIngredients(List<Ingredients> ingredients){
//        return ingredientRepository.saveAll(ingredients);
//    }

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
