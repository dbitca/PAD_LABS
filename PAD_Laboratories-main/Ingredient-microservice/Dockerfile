FROM maven:3.8.3-openjdk-17 AS build
COPY src PAD_Laboratories_main/Ingredient-microservice/src
COPY pom.xml PAD_Laboratories_main/Ingredient-microservice/pom.xml

RUN mvn -f PAD_Laboratories_main/Ingredient-microservice/pom.xml clean

EXPOSE 8080

ENTRYPOINT ["java","-jar","ingredientmicroservice.jar"]