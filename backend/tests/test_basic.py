"""Basic tests for database models and API"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.image_asset import ImageAsset
from app.models.scene_cache import SceneCache
from datetime import datetime, timedelta


@pytest.fixture
def test_db():
    """Create an in-memory test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_image_asset(test_db):
    """Test creating an image asset"""
    asset = ImageAsset(
        component="scene-viewer",
        subject_type="scene",
        subject_name="Test Location",
        prompt_used="A test scene",
        storage_path_full="images/full/test.webp",
        storage_path_thumbnail="images/thumbnails/test.webp",
        file_size_bytes=1024,
        aspect_ratio="16:9",
        generation_time_ms=1000
    )
    test_db.add(asset)
    test_db.commit()

    # Verify
    result = test_db.query(ImageAsset).filter_by(subject_name="Test Location").first()
    assert result is not None
    assert result.subject_name == "Test Location"
    assert result.use_count == 1
    assert result.is_featured == False


def test_create_scene_cache(test_db):
    """Test creating a scene cache entry"""
    # Create image asset first
    asset = ImageAsset(
        component="scene-viewer",
        subject_type="scene",
        subject_name="Emberpeak",
        prompt_used="A fantasy scene",
        storage_path_full="images/full/test.webp",
        storage_path_thumbnail="images/thumbnails/test.webp",
        file_size_bytes=2048,
        aspect_ratio="16:9",
        generation_time_ms=2000
    )
    test_db.add(asset)
    test_db.flush()

    # Create cache entry
    cache = SceneCache(
        location="Emberpeak",
        time_of_day="dawn",
        weather="clear",
        image_asset_id=asset.id,
        expires_at=datetime.now() + timedelta(days=7)
    )
    test_db.add(cache)
    test_db.commit()

    # Verify
    result = test_db.query(SceneCache).filter_by(location="Emberpeak").first()
    assert result is not None
    assert result.location == "Emberpeak"
    assert result.time_of_day == "dawn"
    assert result.use_count == 1


def test_featured_image_toggle(test_db):
    """Test featuring/unfeaturing images"""
    # Create two images for same item
    asset1 = ImageAsset(
        component="item-modal",
        subject_type="item",
        subject_name="Sword",
        prompt_used="A sword",
        storage_path_full="images/full/sword1.webp",
        storage_path_thumbnail="images/thumbnails/sword1.webp",
        file_size_bytes=1024,
        aspect_ratio="1:1",
        generation_time_ms=1000,
        is_featured=True
    )
    asset2 = ImageAsset(
        component="item-modal",
        subject_type="item",
        subject_name="Sword",
        prompt_used="A sword variant",
        storage_path_full="images/full/sword2.webp",
        storage_path_thumbnail="images/thumbnails/sword2.webp",
        file_size_bytes=1024,
        aspect_ratio="1:1",
        generation_time_ms=1000,
        is_featured=False
    )
    test_db.add_all([asset1, asset2])
    test_db.commit()

    # Verify only one is featured
    featured = test_db.query(ImageAsset).filter_by(
        subject_name="Sword",
        is_featured=True
    ).all()
    assert len(featured) == 1
    assert featured[0].id == asset1.id


def test_soft_delete(test_db):
    """Test soft delete functionality"""
    asset = ImageAsset(
        component="scene-viewer",
        subject_type="scene",
        subject_name="Test",
        prompt_used="Test",
        storage_path_full="images/full/test.webp",
        storage_path_thumbnail="images/thumbnails/test.webp",
        file_size_bytes=1024,
        aspect_ratio="16:9",
        generation_time_ms=1000
    )
    test_db.add(asset)
    test_db.commit()

    # Soft delete
    asset.deleted_at = datetime.now()
    test_db.commit()

    # Should still exist in database
    result = test_db.query(ImageAsset).filter_by(id=asset.id).first()
    assert result is not None
    assert result.deleted_at is not None

    # But not in active queries
    active = test_db.query(ImageAsset).filter_by(deleted_at=None).all()
    assert asset not in active

