package com.example.ingredientmicroservice.rest;

import com.example.ingredientmicroservice.domain.RegistrationInfo;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.InetAddress;
import java.net.UnknownHostException;

@Service
public class ServiceRegistration {

    @Value("${service.discovery.url}")
    private String serviceDiscoveryUrl;

    @Value("${server.port}")
    private int servicePort;

    @Value("${spring.application.name}")
    private String serviceName;

//    @Value("${server.address}")
//    private String serviceHost;

    RestTemplate restTemplate = new RestTemplate();

    @PostConstruct
    public void registerService() {
        try {
            String serviceHost = InetAddress.getLocalHost().getHostAddress();
            String registrationUrl = serviceDiscoveryUrl + "/register";
            RegistrationInfo registrationInfo = new RegistrationInfo(serviceName, servicePort, serviceHost);

            restTemplate.postForEntity(registrationUrl, registrationInfo, String.class);
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
    }
}
