package com.example.ingredientmicroservice.domain;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public class RegistrationInfo {
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }

    public int getPort() {
        return port;
    }

    public void setPort(int port) {
        this.port = port;
    }

    public String getHost(){
        return host;
    }

    public void setHost(){
        this.host = host;
    }

    private String name;
    private int port;
    private String host;
}
