import circuitbreaker
from circuitbreaker import CircuitBreaker, CircuitBreakerError
import logging
import requests

class CustomCircuitBreaker(CircuitBreaker):
    FAILURE_THRESHOLD = 1
    RECOVERY_TIMEOUT = 10
    EXPECTED_EXCEPTION = requests.RequestException

    # def __init__(self, max_reroutes=3):
    #     self.error_count = 0
    #     self.max_reroutes = max_reroutes
    #     self.reroute_count = 0
    #
    # def on_success(self):
    #     self.error_count = max(0, self.error_count-1)
    #     self.reroute_count = 0
    #     print("Success. Resetting error count and reroute count.")
    #
    # def on_error(self):
    #     self.reroute_count += 1
    #
    #     if self.error_count >= self.max_errors:
    #         self.reroute_count += 1
    #         self.error_count = 0
    #
    #         if self.reroute_count >= self.max_reroutes:
    #             self.open()
    #             print("Circuit open due to too many errors and reroutes.")
    #
    # def open(self):
    #     print("Circuit open. No requests will be sent.")