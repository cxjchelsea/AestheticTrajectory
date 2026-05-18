from typing import TypeVar

from pydantic import BaseModel


SchemaT = TypeVar("SchemaT", bound=BaseModel)


def validate_structured_output(schema: type[SchemaT], payload: object) -> SchemaT:
    return schema.model_validate(payload)
