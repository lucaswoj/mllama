from typing import List, Optional
from pydantic import BaseModel
import huggingface_hub
from pal.server.bootstrap import server


class TagDetails(BaseModel):
    parent_model: str
    format: str
    family: str
    families: Optional[List[str]]
    parameter_size: str
    quantization_level: str


class TagInfo(BaseModel):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: TagDetails


class TagsResponse(BaseModel):
    models: List[TagInfo]


@server.get("/api/tags")
def tags():
    return TagsResponse(
        models=[
            TagInfo(
                name=f"{repo.repo_id}",
                model=f"{repo.repo_id}",
                modified_at="2024-12-07T13:43:12.129079239-08:00",
                size=repo.size_on_disk,
                digest="3028237cc8c52fea4e77185d72cc997b2e90392791f7c82fe1c71995d56e642d",
                details=TagDetails(
                    format="gguf",
                    parent_model="",
                    family="TODO",
                    families=["TODO"],
                    parameter_size="3B",
                    quantization_level="TODO",
                ),
            )
            for repo in huggingface_hub.scan_cache_dir().repos
        ]
    )
