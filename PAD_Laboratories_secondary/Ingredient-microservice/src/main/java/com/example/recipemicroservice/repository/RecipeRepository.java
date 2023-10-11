package com.example.recipemicroservice.repository;
import com.example.recipemicroservice.domain.Recipes;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface RecipeRepository extends JpaRepository<Recipes, Long>{
    List<Recipes> findByIngredientsContaining(String ingredient);
}
