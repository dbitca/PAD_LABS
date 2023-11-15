import circuitbreaker
from circuitbreaker import CircuitBreaker, CircuitBreakerError
import logging
import requests

class CustomCircuitBreaker(CircuitBreaker):
    FAILURE_THRESHOLD = 2
    RECOVERY_TIMEOUT = 10
    EXPECTED_EXCEPTION = requests.RequestException