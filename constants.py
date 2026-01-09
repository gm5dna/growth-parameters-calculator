"""
Application constants for growth parameters calculator
"""

# Age calculation constants
DAYS_PER_YEAR = 365.25
MONTHS_PER_YEAR = 12.0

# Gestation constants
FULL_TERM_WEEKS = 40
FULL_TERM_DAYS = 280  # 40 weeks * 7 days
MIN_GESTATION_WEEKS = 22
MAX_GESTATION_WEEKS = 44
DAYS_PER_WEEK = 7
MAX_GESTATION_DAYS = 6

# Gestation correction thresholds
PRETERM_THRESHOLD_WEEKS = 37
MODERATE_PRETERM_THRESHOLD_WEEKS = 32
CORRECTION_AGE_THRESHOLD_MODERATE = 1.0  # years
CORRECTION_AGE_THRESHOLD_EXTREME = 2.0  # years

# Validation thresholds
SDS_HARD_LIMIT = 8.0  # Reject measurements beyond ±8 SDS
SDS_WARNING_LIMIT = 4.0  # Warning for measurements beyond ±4 SDS

# Weight validation (kg)
MIN_WEIGHT_KG = 0.1
MAX_WEIGHT_KG = 300.0

# Height validation (cm)
MIN_HEIGHT_CM = 10.0
MAX_HEIGHT_CM = 250.0

# OFC validation (cm)
MIN_OFC_CM = 10.0
MAX_OFC_CM = 100.0

# BSA constants
GH_DOSE_STANDARD = 7.0  # mg/m²/week
WEIGHT_TO_GRAMS = 1000

# Mid-parental height calculation
MPH_ADULT_AGE = 18.0  # years

# Error codes
class ErrorCodes:
    INVALID_DATE_FORMAT = "ERR_001"
    INVALID_DATE_RANGE = "ERR_002"
    MISSING_MEASUREMENT = "ERR_003"
    INVALID_WEIGHT = "ERR_004"
    INVALID_HEIGHT = "ERR_005"
    INVALID_OFC = "ERR_006"
    INVALID_GESTATION = "ERR_007"
    SDS_OUT_OF_RANGE = "ERR_008"
    CALCULATION_ERROR = "ERR_009"
    INVALID_INPUT = "ERR_010"
