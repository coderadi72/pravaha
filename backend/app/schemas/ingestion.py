from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,StrictStr

class FileInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    filename: StrictStr=Field(min_length=1,max_length=255)
    contentBase64: StrictStr=Field(min_length=1,max_length=7_000_000)

class ScheduleImportRequest(FileInput):
    mapping: dict[str,str]=Field(default_factory=dict,max_length=60)
    expectedVersionId: str | None=None
    previewChecksum: str | None=None

class ProviderRequest(BaseModel):
    provider: Literal["ocr","asr","advanced"]

class ProjectCreateRequest(BaseModel):
    name: StrictStr=Field(min_length=1,max_length=150)
    location: StrictStr=Field(default="",max_length=150)
