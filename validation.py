"""
Input validation and sanitization functions
"""
from datetime import date, datetime
from constants import (
    MIN_WEIGHT_KG, MAX_WEIGHT_KG,
    MIN_HEIGHT_CM, MAX_HEIGHT_CM,
    MIN_OFC_CM, MAX_OFC_CM,
    MIN_GESTATION_WEEKS, MAX_GESTATION_WEEKS, MAX_GESTATION_DAYS,
    ErrorCodes
)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)


def validate_date(date_string, field_name):
    """
    Validate and parse date string

    Args:
        date_string: Date in YYYY-MM-DD format
        field_name: Name of field for error messages

    Returns:
        date: Parsed date object

    Raises:
        ValidationError: If date is invalid
    """
    if not date_string:
        raise ValidationError(
            f"{field_name} is required",
            ErrorCodes.INVALID_DATE_FORMAT
        )

    try:
        parsed_date = datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        raise ValidationError(
            f"{field_name} must be in YYYY-MM-DD format",
            ErrorCodes.INVALID_DATE_FORMAT
        )

    # Check date is not in the future
    if parsed_date > date.today():
        raise ValidationError(
            f"{field_name} cannot be in the future",
            ErrorCodes.INVALID_DATE_RANGE
        )

    # Check date is not too far in the past (reasonable limit: 150 years)
    if parsed_date.year < (date.today().year - 150):
        raise ValidationError(
            f"{field_name} is too far in the past",
            ErrorCodes.INVALID_DATE_RANGE
        )

    return parsed_date


def validate_date_range(birth_date, measurement_date):
    """
    Validate that measurement date is after birth date

    Args:
        birth_date: Date of birth
        measurement_date: Date of measurement

    Raises:
        ValidationError: If dates are invalid
    """
    if measurement_date <= birth_date:
        raise ValidationError(
            "Measurement date must be after birth date",
            ErrorCodes.INVALID_DATE_RANGE
        )


def validate_weight(weight):
    """
    Validate weight measurement

    Args:
        weight: Weight in kg (can be None)

    Returns:
        float: Validated weight or None

    Raises:
        ValidationError: If weight is invalid
    """
    if weight is None:
        return None

    try:
        weight_float = float(weight)
    except (ValueError, TypeError):
        raise ValidationError(
            "Weight must be a number",
            ErrorCodes.INVALID_WEIGHT
        )

    if weight_float < MIN_WEIGHT_KG or weight_float > MAX_WEIGHT_KG:
        raise ValidationError(
            f"Weight must be between {MIN_WEIGHT_KG} and {MAX_WEIGHT_KG} kg",
            ErrorCodes.INVALID_WEIGHT
        )

    return weight_float


def validate_height(height):
    """
    Validate height measurement

    Args:
        height: Height in cm (can be None)

    Returns:
        float: Validated height or None

    Raises:
        ValidationError: If height is invalid
    """
    if height is None:
        return None

    try:
        height_float = float(height)
    except (ValueError, TypeError):
        raise ValidationError(
            "Height must be a number",
            ErrorCodes.INVALID_HEIGHT
        )

    if height_float < MIN_HEIGHT_CM or height_float > MAX_HEIGHT_CM:
        raise ValidationError(
            f"Height must be between {MIN_HEIGHT_CM} and {MAX_HEIGHT_CM} cm",
            ErrorCodes.INVALID_HEIGHT
        )

    return height_float


def validate_ofc(ofc):
    """
    Validate OFC (head circumference) measurement

    Args:
        ofc: OFC in cm (can be None)

    Returns:
        float: Validated OFC or None

    Raises:
        ValidationError: If OFC is invalid
    """
    if ofc is None:
        return None

    try:
        ofc_float = float(ofc)
    except (ValueError, TypeError):
        raise ValidationError(
            "Head circumference must be a number",
            ErrorCodes.INVALID_OFC
        )

    if ofc_float < MIN_OFC_CM or ofc_float > MAX_OFC_CM:
        raise ValidationError(
            f"Head circumference must be between {MIN_OFC_CM} and {MAX_OFC_CM} cm",
            ErrorCodes.INVALID_OFC
        )

    return ofc_float


def validate_gestation(gestation_weeks, gestation_days):
    """
    Validate gestation parameters

    Args:
        gestation_weeks: Weeks of gestation (can be None)
        gestation_days: Additional days (can be None)

    Returns:
        tuple: (validated_weeks, validated_days) or (None, None)

    Raises:
        ValidationError: If gestation values are invalid
    """
    if gestation_weeks is None:
        return None, None

    try:
        weeks = int(gestation_weeks)
    except (ValueError, TypeError):
        raise ValidationError(
            "Gestation weeks must be a whole number",
            ErrorCodes.INVALID_GESTATION
        )

    if weeks < MIN_GESTATION_WEEKS or weeks > MAX_GESTATION_WEEKS:
        raise ValidationError(
            f"Gestation weeks must be between {MIN_GESTATION_WEEKS} and {MAX_GESTATION_WEEKS}",
            ErrorCodes.INVALID_GESTATION
        )

    days = 0
    if gestation_days is not None:
        try:
            days = int(gestation_days)
        except (ValueError, TypeError):
            raise ValidationError(
                "Gestation days must be a whole number",
                ErrorCodes.INVALID_GESTATION
            )

        if days < 0 or days > MAX_GESTATION_DAYS:
            raise ValidationError(
                f"Gestation days must be between 0 and {MAX_GESTATION_DAYS}",
                ErrorCodes.INVALID_GESTATION
            )

    return weeks, days


def validate_at_least_one_measurement(weight, height, ofc):
    """
    Validate that at least one measurement is provided

    Args:
        weight: Weight value
        height: Height value
        ofc: OFC value

    Raises:
        ValidationError: If no measurements provided
    """
    if not any([weight, height, ofc]):
        raise ValidationError(
            "At least one measurement (weight, height, or OFC) is required",
            ErrorCodes.MISSING_MEASUREMENT
        )
