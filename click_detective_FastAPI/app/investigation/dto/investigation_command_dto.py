"""행동 입력만 받는 API 형식. 승인 사실·획득 상태·정답을 사용자가 지정하지 못하게 한다."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Key = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)
]


class DTO(BaseModel):
    """오탈자·임의 상태 주입을 막기 위해 정의하지 않은 필드는 거절한다.

    Args:
        없음.

    Returns:
        DTO: 위 역할을 수행하도록 생성된 객체.
    """

    model_config = ConfigDict(extra="forbid")


class NewGame(DTO):
    """새 수사 요청. 같은 요청 UUID는 같은 생성 결과를 재사용한다.

    Args:
        request_id (UUID): 재전송에서도 유지하는 요청 UUID. 같은 작업을 중복 확정하지 않도록 구분한다.
        case_id (Key): 조회하거나 생성할 사건의 식별자.
        scenario_version (Key): 현재 사건 데이터의 스냅샷 버전.

    Returns:
        NewGame: 위 역할을 수행하도록 생성된 객체.
    """

    request_id: UUID
    case_id: Key = "thirteenth-bell-v1"
    scenario_version: Key


class Command(DTO):
    """변경 요청의 공통 키. revision은 현재 공개 상태에서 받은 값을 사용한다.

    Args:
        request_id (UUID): 재전송에서도 유지하는 요청 UUID. 같은 작업을 중복 확정하지 않도록 구분한다.
        expected_revision (int): 사용자가 마지막으로 확인한 수사 상태 버전.

    Returns:
        Command: 위 역할을 수행하도록 생성된 객체.
    """

    request_id: UUID
    expected_revision: int = Field(ge=0)


class Examine(Command):
    """증거를 열람한다. GET으로 상태를 몰래 변경하지 않는다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        evidence_id (Key): 원본 증거의 식별자.

    Returns:
        Examine: 위 역할을 수행하도록 생성된 객체.
    """

    evidence_id: Key


class Interrogate(Command):
    """사용자 심문 입력. 공개 사실과 필수 사실은 서버가 구성한다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        suspect_id (Key): 심문 대상 인물의 식별자.
        question (Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]): 사용자가 입력한 질문 원문.
        material_id (Key | None): 이번 심문에 제시한 자료 식별자.
        topic_id (Key | None): 허용된 질문 주제 식별자. 생략하면 서버가 질문을 분류한다.

    Returns:
        Interrogate: 위 역할을 수행하도록 생성된 객체.
    """

    suspect_id: Key
    question: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
    ]
    material_id: Key | None = None
    topic_id: Key | None = None


class Source(DTO):
    """증거·실제로 기록된 진술·실제로 생성된 추론을 구별하는 출처 참조.

    Args:
        kind (Literal['evidence', 'testimony', 'derived']): 조회할 자료 종류.
        id (Key): 항목을 구분하는 식별자.

    Returns:
        Source: 위 역할을 수행하도록 생성된 객체.
    """

    kind: Literal["evidence", "testimony", "derived"]
    id: Key


class Infer(Command):
    """2~4개의 실제 출처를 정확한 조합으로 연결한다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        sources (list[Source]): 진술과 쟁점의 실제 근거.

    Returns:
        Infer: 위 역할을 수행하도록 생성된 객체.
    """

    sources: list[Source] = Field(min_length=2, max_length=4)


class Advance(Command):
    """다음 단계 요청. 값을 대입하지 않고 서버가 조건을 검사한다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        target_phase (Literal[2]): 전환을 요청할 조사 단계. 현재는 2만 허용한다.

    Returns:
        Advance: 위 역할을 수행하도록 생성된 객체.
    """

    target_phase: Literal[2] = 2


class Notes(Command):
    """메모 전체 저장. 단계·고발 상태를 포함한 공식 상태는 DB가 담당한다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        text (str): 저장할 메모 전체 내용. 최대 20,000자.

    Returns:
        Notes: 위 역할을 수행하도록 생성된 객체.
    """

    text: str = Field(max_length=20000)


class Accuse(Command):
    """고발 선택과 실제 제출할 추론 ID만 받는다.

    Args:
        request_id (UUID): 같은 작업의 재전송을 구분하는 요청 UUID.
        expected_revision (int): 마지막으로 확인한 수사 상태 버전.
        suspect_id (Key): 심문 대상 인물의 식별자.
        motive (Key): 고발할 범행 동기의 선택지 ID.
        method (Key): 고발할 범행 방법의 선택지 ID.
        evidence_ids (list[Key]): 고발의 근거로 제출할 실제 획득 추론 증거 ID 목록.

    Returns:
        Accuse: 위 역할을 수행하도록 생성된 객체.
    """

    suspect_id: Key
    motive: Key
    method: Key
    evidence_ids: list[Key] = Field(default_factory=list, max_length=50)
