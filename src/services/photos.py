from fastapi import HTTPException

ALLOWED_CROP_MODES = ("fill", "thumb", "fit", "limit", "pad", "scale", None)
ALLOWED_GRAVITY_MODES = ("center", "north", "north_east", "east", "south_east",
                         "south", "south_west", "west", "north_west", "auto", None)


def validate_crop_mode(crop_mode):
    if crop_mode in ALLOWED_CROP_MODES:
        return True
    raise HTTPException(
        status_code=400,
        detail=f"Invalid crop mode. Allowed crop modes are: {', '.join(ALLOWED_CROP_MODES)}"
    )


def validate_gravity_mode(gravity_mode):
    if gravity_mode in ALLOWED_GRAVITY_MODES:
        return True
    raise HTTPException(
        status_code=400,
        detail=f"Invalid gravity mode. Allowed gravity modes are: {', '.join(ALLOWED_GRAVITY_MODES)}"
    )
