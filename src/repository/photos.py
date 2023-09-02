from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from fastapi import HTTPException, status
from src.conf.config import init_cloudinary
from src.conf.messages import YOUR_PHOTO,ALREADY_LIKE
from src.database.models import User, Role, BlacklistToken, Post, Rating, Photo,QR_code
import qrcode
import os

async def created_photo(url,curent_user,db:AsyncSession):
    photo= Photo(url=url,description='TEST',user_id=curent_user.id)

    db.add(photo)
    await db.commit()
    await db.refresh(photo)

    return photo

async def get_URL_Qr(photo_id:int,db:AsyncSession):

    query = select(Photo).filter(Photo.id == photo_id)

    result = await db.execute(query)
    photo = result.scalar()

    query = select(QR_code).filter(QR_code.photo_id == photo_id)

    result = await db.execute(query)
    qr = result.scalar()
    if qr != None:
        return {"source_url": photo.url, "qr_code_url": qr.url}

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(photo.url)

    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    qr_code_file_path = "my_qr_code.png"
    img.save(qr_code_file_path)

    init_cloudinary()
    upload_result = cloudinary.uploader.upload(
        qr_code_file_path,
        public_id=f"Qr_Code/Photo_{photo_id}",
        overwrite=True,
        invalidate=True,
    )
    qr= QR_code(url=upload_result["secure_url"],photo_id=photo_id)

    db.add(qr)
    await db.commit()
    await db.refresh(qr)


    os.remove(qr_code_file_path)

    return {"source_url": photo.url, "qr_code_url": qr.url}

