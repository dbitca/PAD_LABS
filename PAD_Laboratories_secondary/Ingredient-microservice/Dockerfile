FROM maven:3.8.3-openjdk-17 AS build
FROM openjdk:17-jdk-alpine

ARG JAR_FILE=target/*.jar
COPY ./target/Ingredient-microservice-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java","-jar","/app.jar"]