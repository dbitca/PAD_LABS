package com.example.ingredientmicroservice.repository;
import com.example.ingredientmicroservice.domain.Ingredients;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface IngredientRepository extends JpaRepository<Ingredients, Long>{
}
