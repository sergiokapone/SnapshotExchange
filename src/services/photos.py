from fastapi import HTTPException

ALLOWED_CROP_MODES = ("fill", "thumb", "fit", "limit", "pad", "scale", None)
ALLOWED_GRAVITY_MODES = (
    "center",
    "north",
    "north_east",
    "east",
    "south_east",
    "south",
    "south_west",
    "west",
    "north_west",
    "auto",
    None,
)


def validate_crop_mode(crop_mode):
    """
    Validate Crop Mode

    This function validates if a given crop mode is one of the allowed crop modes.

    :param crop_mode: The crop mode to be validated.
    :type crop_mode: str
    :return: True if the crop mode is valid.
    :rtype: bool
    :raises HTTPException 400: If the crop mode is not in the list of allowed crop modes.

    **Example Usage:**

    .. code-block:: python

        validate_crop_mode('square')  # Returns True

    """

    if crop_mode in ALLOWED_CROP_MODES:
        return True
    allowed_modes = [mode for mode in ALLOWED_CROP_MODES if mode is not None]
    raise HTTPException(
        status_code=400,
        detail=f"Invalid crop mode. Allowed crop modes are: {', '.join(allowed_modes)}",
    )


def validate_gravity_mode(gravity_mode):
    """
    Validate Gravity Mode

    This function validates if a given gravity mode is one of the allowed gravity modes.

    :param gravity_mode: The gravity mode to be validated.
    :type gravity_mode: str
    :return: True if the gravity mode is valid.
    :rtype: bool
    :raises HTTPException 400: If the gravity mode is not in the list of allowed gravity modes.

    **Example Usage:**

    .. code-block:: python

        validate_gravity_mode('center')  # Returns True

    """

    if gravity_mode in ALLOWED_GRAVITY_MODES:
        return True
    allowed_modes = [mode for mode in ALLOWED_GRAVITY_MODES if mode is not None]
    raise HTTPException(
        status_code=400,
        detail=f"Invalid gravity mode. Allowed gravity modes are: {', '.join(allowed_modes)}",
    )
