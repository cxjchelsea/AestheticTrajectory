from app.schemas.common import new_id, utc_now
from app.schemas.input import AestheticInputResponse, CreateInputRequest


class InputService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def create_input(self, request: CreateInputRequest) -> AestheticInputResponse:
        input_record = AestheticInputResponse(
            id=new_id("input"),
            userId="user_anonymous",
            type=request.type,
            contentText=request.content_text,
            fileUrl=request.file_url,
            source=request.source,
            title=request.title,
            description=request.description,
            createdAt=utc_now(),
        )
        return self.repository.save(input_record)
