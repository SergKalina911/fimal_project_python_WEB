""" Photo routes """

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

from app.models.tag import photo_tags, Tag
from app.core.database import get_db
from app.models.photo import Photo, PhotoTransform
from app.models.user import User, Role
from app.schemas import PhotoRead
from app.core.security import require_user
from app.services.cloudinary_service import upload_image, upload_bytes, transform_image
from app.services.qr_service import QRService
from app.routes.users import user_to_schema

router = APIRouter(prefix="/photos", tags=["Photos"])

# --- завантаження фото ---
@router.post("/", response_model=PhotoRead)
async def upload_photo(
    file: UploadFile = File(...),
    description: str = Form(None),
    tag_names: list[str] = Form([], description="Теги для фото (максимум 5, можна через кому)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = upload_image(file)
    if not result or "secure_url" not in result or "public_id" not in result:
        raise HTTPException(status_code=500, detail="Image upload failed")

    new_photo = Photo(
        url=result["secure_url"],
        public_id=result["public_id"],
        description=description,
        user_id=current_user.id,
        status="new"
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    parsed_tags = []
    for name in tag_names:
        parsed_tags.extend([t.strip() for t in name.split(",") if t.strip()])

    if parsed_tags:
        existing_tags = await db.execute(select(photo_tags).where(photo_tags.c.photo_id == new_photo.id))
        existing_count = len(existing_tags.fetchall())
        if existing_count + len(parsed_tags) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 tags allowed per photo")
        
        for name in parsed_tags:
            tag_result = await db.execute(select(Tag).where(Tag.name == name))
            tag = tag_result.scalars().first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            await db.execute(photo_tags.insert().values(photo_id=new_photo.id, tag_id=tag.id))
        await db.commit()
        await db.refresh(new_photo)

    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.transforms),
            joinedload(Photo.comments),
            joinedload(Photo.owner)
        ).where(Photo.id == new_photo.id)
    )
    photo_with_relations = result.scalars().first()

    owner_schema = await user_to_schema(db, photo_with_relations.owner)
    photo_dict = PhotoRead.model_validate(photo_with_relations).dict()
    photo_dict["owner"] = owner_schema

    return PhotoRead.model_validate(photo_dict)


# --- модерація фото ---
@router.put("/{photo_id}/moderate", response_model=PhotoRead)
async def moderate_photo(
    photo_id: int,
    transformation: str = Form(..., description="Тип трансформації", enum=["resize","circle","text"]),
    tag_names: list[str] = Form([], description="Нові теги (максимум 5, можна через кому)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # 🔹 дозволяємо власнику або модератору/адміну
    if photo.user_id != current_user.id and current_user.role not in [Role.ADMIN, Role.MODERATOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    photo.status = "moderation"

    allowed_transformations = {
        "resize": [{"width": 300, "height": 300, "crop": "fill", "gravity": "auto"}],
        "circle": [{"radius": "max", "crop": "fill"}],
        "text": [{"overlay": {"font_family": "Arial", "font_size": 30, "text": "Sample"}}],
    }
    if transformation not in allowed_transformations:
        raise HTTPException(status_code=400, detail=f"Invalid transformation. Allowed: {list(allowed_transformations.keys())}")

    transformed_url = transform_image(photo.public_id, transformation=allowed_transformations[transformation])
    if not transformed_url:
        raise HTTPException(status_code=500, detail="Image transformation failed")

    new_photo = Photo(
        url=transformed_url,
        public_id=photo.public_id,
        description=f"Transformed version of photo {photo_id}",
        user_id=photo.user_id,
        status="approved"
    )
    db.add(new_photo)
    await db.commit()
    await db.refresh(new_photo)

    parsed_tags = []
    for name in tag_names:
        parsed_tags.extend([t.strip() for t in name.split(",") if t.strip()])

    if parsed_tags:
        existing_tags = await db.execute(select(photo_tags).where(photo_tags.c.photo_id == new_photo.id))
        existing_count = len(existing_tags.fetchall())
        if existing_count + len(parsed_tags) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 tags allowed per photo")
        for name in parsed_tags:
            tag_result = await db.execute(select(Tag).where(Tag.name == name))
            tag = tag_result.scalars().first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            await db.execute(photo_tags.insert().values(photo_id=new_photo.id, tag_id=tag.id))
        await db.commit()
    else:
        for tag in photo.tags:
            await db.execute(photo_tags.insert().values(photo_id=new_photo.id, tag_id=tag.id))
        await db.commit()
    
    qr_buffer = QRService.generate_qr(new_photo.url)
    qr_result = upload_bytes(qr_buffer, folder="qr_codes")
    if not qr_result or "secure_url" not in qr_result:
        raise HTTPException(status_code=500, detail="QR upload failed")

    transform_record = PhotoTransform(
        photo_id=new_photo.id,
        transformed_url=new_photo.url,
        qr_url=qr_result["secure_url"]
    )
    db.add(transform_record)
    await db.commit()
    await db.refresh(transform_record)
    await db.refresh(new_photo)

    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.transforms),
            joinedload(Photo.comments),
            joinedload(Photo.owner)
        ).where(Photo.id == new_photo.id)
    )
    photo_with_relations = result.scalars().first()

    owner_schema = await user_to_schema(db, photo_with_relations.owner)
    photo_dict = PhotoRead.model_validate(photo_with_relations).dict()
    photo_dict["owner"] = owner_schema

    return PhotoRead.model_validate(photo_dict)

# --- редагування фото ---
@router.put(
    "/{photo_id}",
    response_model=PhotoRead,
    description="Оновлює опис фото та замінює всі теги на нові (старі видаляються)."
)
# 🔹 ВАЖЛИВО: тут відбувається повна заміна тегів — старі видаляються
async def update_photo(
    photo_id: int,
    description: str = Form(...),
    tag_names: list[str] = Form([], description="Оновлені теги (максимум 5, можна через кому)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if photo.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 🔹 оновлюємо опис
    photo.description = description

    # 🔹 розбиваємо теги по комі
    parsed_tags = []
    for name in tag_names:
        parsed_tags.extend([t.strip() for t in name.split(",") if t.strip()])

    if parsed_tags:
        # перевірка сумарної кількості тегів
        existing_tags = await db.execute(select(photo_tags).where(photo_tags.c.photo_id == photo.id))
        existing_count = len(existing_tags.fetchall())
        if existing_count + len(parsed_tags) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 tags allowed per photo")

        # очищаємо старі зв’язки
        await db.execute(photo_tags.delete().where(photo_tags.c.photo_id == photo.id))

        for name in parsed_tags:
            tag_result = await db.execute(select(Tag).where(Tag.name == name))
            tag = tag_result.scalars().first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                await db.commit()
                await db.refresh(tag)
            await db.execute(photo_tags.insert().values(photo_id=photo.id, tag_id=tag.id))
        await db.commit()
        await db.refresh(photo)

    await db.commit()
    await db.refresh(photo)

    # 🔹 підтягнути всі зв’язки
    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.transforms),
            joinedload(Photo.comments),
            joinedload(Photo.owner)
        ).where(Photo.id == photo.id)
    )
    photo_with_relations = result.scalars().first()

    # 🔹 серіалізуємо owner через user_to_schema
    owner_schema = await user_to_schema(db, photo_with_relations.owner)
    photo_dict = PhotoRead.model_validate(photo_with_relations).dict()
    photo_dict["owner"] = owner_schema

    return PhotoRead.model_validate(photo_dict)

# --- видалення фото ---
@router.delete("/{photo_id}", response_model=dict)
async def delete_photo(
    photo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if photo.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await db.delete(photo)
    await db.commit()
    db.expire_all()

    return {"detail": f"Photo {photo_id} deleted successfully"}

# --- додавання тегів ---
@router.post(
    "/{photo_id}/tags",
    response_model=PhotoRead,
    description="Додає нові теги до фото без видалення існуючих."
)
async def add_tags(
    photo_id: int,
    tag_names: list[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    # 🔹 Тут додаються нові теги без видалення існуючих
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if photo.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 🔹 розбиваємо теги по комі
    parsed_tags = []
    for name in tag_names:
        parsed_tags.extend([t.strip() for t in name.split(",") if t.strip()])

    # перевірка сумарної кількості тегів
    existing_tags = await db.execute(select(photo_tags).where(photo_tags.c.photo_id == photo.id))
    existing_count = len(existing_tags.fetchall())
    if existing_count + len(parsed_tags) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 tags allowed per photo")

    for name in parsed_tags:
        tag_result = await db.execute(select(Tag).where(Tag.name == name))
        tag = tag_result.scalars().first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            await db.commit()
            await db.refresh(tag)
        await db.execute(photo_tags.insert().values(photo_id=photo.id, tag_id=tag.id))
    await db.commit()
    await db.refresh(photo)

    # 🔹 підтягнути всі зв’язки
    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.transforms),
            joinedload(Photo.comments),
            joinedload(Photo.owner)
        ).where(Photo.id == photo.id)
    )
    photo_with_relations = result.scalars().first()

    # 🔹 серіалізуємо owner через user_to_schema
    owner_schema = await user_to_schema(db, photo_with_relations.owner)
    photo_dict = PhotoRead.model_validate(photo_with_relations).dict()
    photo_dict["owner"] = owner_schema

    return PhotoRead.model_validate(photo_dict)

# --- видалення тегу з фото ---
@router.delete("/{photo_id}/tags/{tag_id}", response_model=PhotoRead)
async def delete_photo_tag(
    photo_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_user)
):
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalars().first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo.user_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # перевіряємо чи існує зв’язок фото ↔ тег
    existing_link = await db.execute(
        select(photo_tags).where(
            and_(
                photo_tags.c.photo_id == photo_id,
                photo_tags.c.tag_id == tag_id
            )
        )
    )
    if not existing_link.first():
        raise HTTPException(status_code=404, detail="Tag not attached to this photo")

    await db.execute(
        photo_tags.delete().where(
            and_(
                photo_tags.c.photo_id == photo_id,
                photo_tags.c.tag_id == tag_id
            )
        )
    )
    await db.commit()
    db.expire_all()

    # повторно підтягнути фото з усіма зв’язками
    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.comments),
            joinedload(Photo.transforms),
            joinedload(Photo.owner)
        ).where(Photo.id == photo_id)
    )
    photo_with_relations = result.unique().scalars().first()

    owner_schema = await user_to_schema(db, photo_with_relations.owner)
    photo_dict = PhotoRead.model_validate(photo_with_relations).dict()
    photo_dict["owner"] = owner_schema

    return PhotoRead.model_validate(photo_dict)

# --- отримання фото користувача ---
@router.get("/user/{user_id}", response_model=list[PhotoRead])
async def get_user_photos(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Photo).options(
            joinedload(Photo.tags),
            joinedload(Photo.comments),
            joinedload(Photo.transforms),
            joinedload(Photo.owner)
        ).where(Photo.user_id == user_id)
    )
    photos = result.unique().scalars().all()

    photo_list = []
    for photo in photos:
        owner_schema = await user_to_schema(db, photo.owner)
        photo_dict = PhotoRead.model_validate(photo).dict()
        photo_dict["owner"] = owner_schema
        photo_list.append(PhotoRead.model_validate(photo_dict))

    return photo_list
