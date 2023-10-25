FROM maven:3.8.3-openjdk-17 AS build
COPY src PAD_Laboratories_secondary/Ingredient-microservice/src
COPY pom.xml PAD_Laboratories_secondary/Ingredient-microservice/pom.xml

RUN mvn -f PAD_Laboratories_secondary/Ingredient-microservice/pom.xml clean

EXPOSE 8081

RUN ["ls"]
RUN ["java","-jar","target/Ingredient-microservice-0.0.1-SNAPSHOT.jar"]