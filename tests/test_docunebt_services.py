import unittest
from unittest.mock import AsyncMock,MagicMock,patch
from sqlalchemy.ext.asyncio import AsyncSession
import sys
import os  
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import HTTPException
from datetime import datetime, timedelta
from src.database.models import Rating,Photo,User,Tag
from src.schemas import UserSchema
from src.services.auth import Auth

