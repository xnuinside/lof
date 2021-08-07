from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Context(BaseModel):

    function_name: str = "MockLambdaName"
    function_version: str = "latest"
    invoked_function_arn: str = "invoked_function_arn"
    memory_limit_in_mb: int = 500
    aws_request_id: UUID = Field(default=str(uuid4()))
    log_group_name: str = "log_group_name"
    log_stream_name: str = "log_stream_name"
    identity: UUID = Field(default=str(uuid4()))
    cognito_identity_id: UUID = Field(default=str(uuid4()))
    cognito_identity_pool_id: UUID = Field(default=str(uuid4()))

    @staticmethod
    def get_remaining_time_in_millis():
        return 4200
