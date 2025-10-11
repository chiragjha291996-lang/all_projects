# sensor_thresholds.py
"""
Centralized sensor threshold configuration for consistent alerting across all equipment.
This ensures uniform thresholds regardless of equipment type or base values.
"""

class SensorThresholds:
    """Centralized sensor thresholds for all equipment types"""
    
    # Temperature thresholds (°C)
    TEMPERATURE = {
        'critical_high': 110,    # Critical alert threshold
        'warning_high': 95,      # Warning alert threshold
        'normal_max': 85,        # Normal operating range max
        'normal_min': 60,        # Normal operating range min
        'warning_low': 50,       # Warning alert threshold (low)
        'critical_low': 40       # Critical alert threshold (low)
    }
    
    # Vibration thresholds (mm/s)
    VIBRATION = {
        'critical_high': 8.0,   # Critical alert threshold
        'warning_high': 6.0,    # Warning alert threshold
        'normal_max': 4.0,      # Normal operating range max
        'normal_min': 0.5,      # Normal operating range min
        'warning_low': 0.2,     # Warning alert threshold (low)
        'critical_low': 0.1     # Critical alert threshold (low)
    }
    
    # Pressure thresholds (bar)
    PRESSURE = {
        'critical_high': 45,    # Critical alert threshold
        'warning_high': 40,      # Warning alert threshold
        'normal_max': 35,        # Normal operating range max
        'normal_min': 15,        # Normal operating range min
        'warning_low': 10,       # Warning alert threshold (low)
        'critical_low': 5        # Critical alert threshold (low)
    }
    
    # RPM thresholds (RPM)
    RPM = {
        'critical_high': 2500,  # Critical alert threshold
        'warning_high': 2300,   # Warning alert threshold
        'normal_max': 2200,     # Normal operating range max
        'normal_min': 1200,     # Normal operating range min
        'warning_low': 1000,    # Warning alert threshold (low)
        'critical_low': 800     # Critical alert threshold (low)
    }
    
    # Health score thresholds (%)
    HEALTH_SCORE = {
        'critical_low': 20,     # Critical alert threshold
        'warning_low': 40,      # Warning alert threshold
        'normal_min': 60,       # Normal operating range min
        'normal_max': 100,      # Normal operating range max
        'excellent_min': 90     # Excellent condition threshold
    }
    
    # Failure probability thresholds (%)
    FAILURE_PROBABILITY = {
        'critical_high': 70,    # Critical alert threshold
        'warning_high': 50,     # Warning alert threshold
        'normal_max': 30,       # Normal operating range max
        'normal_min': 0,        # Normal operating range min
        'low_max': 10           # Low risk threshold
    }
    
    @classmethod
    def get_temperature_status(cls, value):
        """Get temperature status based on thresholds"""
        if value >= cls.TEMPERATURE['critical_high'] or value <= cls.TEMPERATURE['critical_low']:
            return 'critical'
        elif value >= cls.TEMPERATURE['warning_high'] or value <= cls.TEMPERATURE['warning_low']:
            return 'warning'
        else:
            return 'normal'
    
    @classmethod
    def get_vibration_status(cls, value):
        """Get vibration status based on thresholds"""
        if value >= cls.VIBRATION['critical_high'] or value <= cls.VIBRATION['critical_low']:
            return 'critical'
        elif value >= cls.VIBRATION['warning_high'] or value <= cls.VIBRATION['warning_low']:
            return 'warning'
        else:
            return 'normal'
    
    @classmethod
    def get_pressure_status(cls, value):
        """Get pressure status based on thresholds"""
        if value >= cls.PRESSURE['critical_high'] or value <= cls.PRESSURE['critical_low']:
            return 'critical'
        elif value >= cls.PRESSURE['warning_high'] or value <= cls.PRESSURE['warning_low']:
            return 'warning'
        else:
            return 'normal'
    
    @classmethod
    def get_rpm_status(cls, value):
        """Get RPM status based on thresholds"""
        if value >= cls.RPM['critical_high'] or value <= cls.RPM['critical_low']:
            return 'critical'
        elif value >= cls.RPM['warning_high'] or value <= cls.RPM['warning_low']:
            return 'warning'
        else:
            return 'normal'
    
    @classmethod
    def get_health_status(cls, value):
        """Get health score status based on thresholds"""
        if value <= cls.HEALTH_SCORE['critical_low']:
            return 'critical'
        elif value <= cls.HEALTH_SCORE['warning_low']:
            return 'warning'
        elif value >= cls.HEALTH_SCORE['excellent_min']:
            return 'excellent'
        else:
            return 'normal'
    
    @classmethod
    def get_failure_probability_status(cls, value):
        """Get failure probability status based on thresholds"""
        if value >= cls.FAILURE_PROBABILITY['critical_high']:
            return 'critical'
        elif value >= cls.FAILURE_PROBABILITY['warning_high']:
            return 'warning'
        elif value <= cls.FAILURE_PROBABILITY['low_max']:
            return 'low'
        else:
            return 'normal'
    
    @classmethod
    def get_all_thresholds(cls):
        """Get all thresholds as a dictionary for API responses"""
        return {
            'temperature': cls.TEMPERATURE,
            'vibration': cls.VIBRATION,
            'pressure': cls.PRESSURE,
            'rpm': cls.RPM,
            'health_score': cls.HEALTH_SCORE,
            'failure_probability': cls.FAILURE_PROBABILITY
        }
    
    @classmethod
    def validate_sensor_value(cls, sensor_type, value):
        """Validate if sensor value is within acceptable range"""
        thresholds = getattr(cls, sensor_type.upper())
        
        if sensor_type == 'temperature':
            return thresholds['critical_low'] <= value <= thresholds['critical_high']
        elif sensor_type == 'vibration':
            return thresholds['critical_low'] <= value <= thresholds['critical_high']
        elif sensor_type == 'pressure':
            return thresholds['critical_low'] <= value <= thresholds['critical_high']
        elif sensor_type == 'rpm':
            return thresholds['critical_low'] <= value <= thresholds['critical_high']
        
        return True  # Unknown sensor type, assume valid
