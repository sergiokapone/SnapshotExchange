import unittest
import sys
import os  
import asyncio
from starlette.exceptions import HTTPException  
from unittest.mock import Mock, ANY,patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.photos import validate_crop_mode, validate_gravity_mode



class TestValidationFunctions(unittest.TestCase):

    def test_valid_crop_mode(self):
        crop_mode = "fill"
        self.assertTrue(validate_crop_mode(crop_mode))

    def test_invalid_crop_mode(self):
        crop_mode = "invalid_mode"
        with self.assertRaises(HTTPException) as context:
            validate_crop_mode(crop_mode)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid crop mode", context.exception.detail)

    def test_valid_gravity_mode(self):
        gravity_mode = "center"
        self.assertTrue(validate_gravity_mode(gravity_mode))

    def test_invalid_gravity_mode(self):
        gravity_mode = "invalid_mode"
        with self.assertRaises(HTTPException) as context:
            validate_gravity_mode(gravity_mode)
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Invalid gravity mode", context.exception.detail)

    def test_none_crop_mode(self):
        crop_mode = None
        self.assertTrue(validate_crop_mode(crop_mode))

    def test_none_gravity_mode(self):
        gravity_mode = None
        self.assertTrue(validate_gravity_mode(gravity_mode))

if __name__ == "__main__":
    unittest.main()