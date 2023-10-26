package com.example.recipemicroservice.domain;


import jakarta.persistence.*;
import lombok.*;

import java.util.List;


@Data
@Entity
@Table(name = "recipes")
@NoArgsConstructor
@AllArgsConstructor
public class Recipes {
    @Id
    @GeneratedValue
    private Long id;

    @Column(name = "recipe_id", unique = true)
    private String recipeId;

    @Column (name = "name")
    private String name;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "ingredients", joinColumns = @JoinColumn(name = "recipe_id"))
    @Column(name = "ingredient_id")
    private List<String> ingredients;

    @Column(name = "instructions")
    private String instructions;

}
