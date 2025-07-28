"""
Custom exceptions for aRdent ScanPad library

Provides specific exception types for different error conditions
to enable better error handling in user applications.
"""

class ScanPadError(Exception):
    """Base exception for all aRdent ScanPad errors"""
    pass


class ConnectionError(ScanPadError):
    """Raised when BLE connection issues occur"""
    def __init__(self, message: str = "Failed to connect to ScanPad device"):
        super().__init__(message)
        self.message = message


class DeviceNotFoundError(ConnectionError):
    """Raised when no ScanPad device is found during discovery"""
    def __init__(self, message: str = "No aRdent ScanPad device found"):
        super().__init__(message)


class TimeoutError(ScanPadError):
    """Raised when operations timeout"""
    def __init__(self, message: str = "Operation timed out", timeout_seconds: float = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


class ConfigurationError(ScanPadError):
    """Raised when device configuration fails"""
    def __init__(self, message: str = "Configuration operation failed"):
        super().__init__(message)


class InvalidParameterError(ScanPadError):
    """Raised when invalid parameters are provided"""
    def __init__(self, parameter: str, value, message: str = None):
        if message is None:
            message = f"Invalid parameter '{parameter}': {value}"
        super().__init__(message)
        self.parameter = parameter
        self.value = value


class NotificationError(ScanPadError):
    """Raised when BLE notification setup fails"""
    def __init__(self, message: str = "Failed to setup BLE notifications"):
        super().__init__(message)


class FirmwareError(ScanPadError):
    """Raised when firmware-related operations fail"""
    def __init__(self, message: str = "Firmware operation failed"):
        super().__init__(message)


class ValidationError(ScanPadError):
    """Raised when data validation fails"""
    def __init__(self, message: str = "Data validation failed"):
        super().__init__(message)


class OTAError(ScanPadError):
    """Raised when OTA update operations fail"""
    def __init__(self, message: str = "OTA operation failed"):
        super().__init__(message)


class AuthenticationError(ScanPadError):
    """Raised when authentication fails (API key, credentials, etc.)"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class NetworkError(ScanPadError):
    """Raised when network operations fail"""
    def __init__(self, message: str = "Network operation failed"):
        super().__init__(message)