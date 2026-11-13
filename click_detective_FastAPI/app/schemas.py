"""행동 입력만 받는 API 형식. 승인 사실·획득 상태·정답을 사용자가 지정하지 못하게 한다."""

from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Key = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]


class DTO(BaseModel):
    """오탈자·임의 상태 주입을 막기 위해 정의하지 않은 필드는 거절한다."""
    model_config = ConfigDict(extra="forbid")


class NewGame(DTO):
    """새 수사 요청. 같은 요청 UUID는 같은 생성 결과를 재사용한다."""
    request_id: UUID
    case_id: Key = "thirteenth-bell-v1"
    scenario_version: Key


class Command(DTO):
    """변경 요청의 공통 키. revision은 현재 공개 상태에서 받은 값을 사용한다."""
    request_id: UUID
    expected_revision: int = Field(ge=0)


class Examine(Command):
    """증거를 열람한다. GET으로 상태를 몰래 변경하지 않는다."""
    evidence_id: Key


class Interrogate(Command):
    """사용자 심문 입력. 공개 사실과 필수 사실은 서버가 구성한다."""
    suspect_id: Key
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    material_id: Key | None = None
    topic_id: Key | None = None


class Source(DTO):
    """증거·실제로 기록된 진술·실제로 생성된 추론을 구별하는 출처 참조."""
    kind: Literal["evidence", "testimony", "derived"]
    id: Key


class Infer(Command):
    """2~4개의 실제 출처를 정확한 조합으로 연결한다."""
    sources: list[Source] = Field(min_length=2, max_length=4)


class Advance(Command):
    """다음 단계 요청. 값을 대입하지 않고 서버가 조건을 검사한다."""
    target_phase: Literal[2] = 2


class Notes(Command):
    """메모 전체 저장. 단계·고발 상태를 포함한 공식 상태는 DB가 담당한다."""
    text: str = Field(max_length=20000)


class Accuse(Command):
    """고발 선택과 실제 제출할 추론 ID만 받는다."""
    suspect_id: Key
    motive: Key
    method: Key
    evidence_ids: list[Key] = Field(default_factory=list, max_length=50)
