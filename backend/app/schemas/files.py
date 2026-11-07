from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FileUploadResponse(BaseModel):
    file_id: str
    original_filename: str
    stored_filename: str
    mime_type: str
    file_category: str
    file_size_bytes: int
    extracted_text_preview: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
