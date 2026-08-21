from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.tag import photo_tags, Tag
from app.core.database import get_db
from app.models.photo import Photo
from app.models.user import User
from app.schemas import PhotoRead
from app.core.security import require_user, require_moderator, require_admin
from app.services.cloudinary_service import upload_image, transform_image
from app.services.qr_service import QRService   # 🔹 додано для QR-коду

router = APIRouter(prefix="/photos", tags=["Photos"])

# --- створення фото ---
@router.post("/", response_model=PhotoRead)
async def upload_photo(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    url = upload_image(file)

    new_photo = Photo(
        url=url,
        description=description,
        user_id=current_user.id,
        status="new"   # 🔹 статус тепер видно у відповіді
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)
    return new_photo


# --- перегляд фото ---
@router.get("/{photo_id}", response_model=PhotoRead)
async def get_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


# --- модерація + трансформація фото ---
@router.put("/{photo_id}/moderate")
async def moderate_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_moderator)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

    # позначаємо фото як "moderation"
    photo.status = "moderation"
    db.add(photo)

    # 🔹 трансформація через Cloudinary URL
    transformed_url = transform_image(
        photo.url,
        transformation=[{"width": 300, "height": 300, "crop": "fill", "gravity": "auto"}]
    )

    # створюємо новий запис у БД
    new_photo = Photo(
        url=transformed_url,
        description=f"Transformed version of photo {photo_id}",
        user_id=photo.user_id,
        status="approved"
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    # 🔹 копіюємо теги зі старого фото
    for tag in photo.tags:
        await db.execute(photo_tags.insert().values(photo_id=new_photo.id, tag_id=tag.id))
    await db.commit()

    # 🔹 генеруємо QR-код для нового фото
    qr_buffer = QRService.generate_qr(new_photo.url)
    qr_url = upload_image(UploadFile(file=qr_buffer), folder="qr_codes")

    return {
        "detail": "Photo transformed and flagged for moderation",
        "new_photo_id": new_photo.id,
        "new_url": new_photo.url,
        "status": new_photo.status,   # 🔹 тепер повертаємо статус
        "qr_url": qr_url              # 🔹 повертаємо QR-код
    }
