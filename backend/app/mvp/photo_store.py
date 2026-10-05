import json
import os
import logging
from typing import List, Optional, Dict
from backend.app.config import settings
from backend.app.mvp.schemas import PhotoRecord, PhotoLocation

logger = logging.getLogger(__name__)

class PhotoStore:
    _instance = None
    
    def __init__(self):
        self.photos: List[PhotoRecord] = []
        self.photo_map: Dict[str, PhotoRecord] = {}
        self.load_metadata()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PhotoStore()
        return cls._instance
        
    def load_metadata(self):
        metadata_path = settings.METADATA_PATH
        if not os.path.exists(metadata_path):
            logger.error(f"Metadata file not found at {metadata_path}")
            return
            
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                
            self.photos = []
            self.photo_map = {}
            for item in raw_data:
                loc_data = item.get("location", {})
                location_obj = PhotoLocation(
                    city=loc_data.get("city", ""),
                    state=loc_data.get("state", ""),
                    country=loc_data.get("country", ""),
                    landmark=loc_data.get("landmark", "")
                )
                
                record = PhotoRecord(
                    photo_id=item["photo_id"],
                    filename=item["filename"],
                    image_url=item["image_url"],
                    date=item["date"],
                    year=item["year"],
                    month=item.get("month", 1),
                    season=item.get("season", ""),
                    location=location_obj,
                    people=item.get("people", []),
                    people_relationships=item.get("people_relationships", []),
                    event=item.get("event", ""),
                    objects=item.get("objects", []),
                    visual_concepts=item.get("visual_concepts", []),
                    visual_semantics=item.get("visual_semantics"),
                    ocr_text=item.get("ocr_text", ""),
                    album=item.get("album", ""),
                    is_favorite=item.get("is_favorite", False),
                    description=item.get("description", "")
                )

                self.photos.append(record)
                self.photo_map[record.photo_id] = record
                
            logger.info(f"Loaded {len(self.photos)} photos into PhotoStore.")
        except Exception as e:
            logger.error(f"Failed to load photo metadata: {e}")
            
    def get_all_photos(self) -> List[PhotoRecord]:
        return self.photos
        
    def get_photo_by_id(self, photo_id: str) -> Optional[PhotoRecord]:
        return self.photo_map.get(photo_id)

def get_photo_store() -> PhotoStore:
    return PhotoStore.get_instance()
