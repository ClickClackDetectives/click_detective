"""investigation/test_api_routes.py의 회귀 동작을 확인한다."""


def test_all_business_routes_have_coverage(api):
    """새 API가 생기면 검사 목록을 함께 갱신하도록 OpenAPI 경로를 확인한다.

    Args:
        api: 인증과 응답 기록을 처리하는 테스트용 API 호출 함수.

    Returns:
        None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
    """
    response = api("GET", "/openapi.json", authenticated=False)
    assert response.status_code == 200
    actual = {
        (method.upper(), path)
        for path, methods in response.json()["paths"].items()
        for method in methods
        if method in {"get", "post", "put", "patch", "delete"}
    }
    expected = {
        ("GET", "/healthz"),
        ("GET", "/v1/catalog"),
        ("GET", "/v1/cases"),
        ("GET", "/v1/cases/{case_id}"),
        ("GET", "/v1/assets/{asset_path}"),
        ("POST", "/v1/games"),
        ("GET", "/v1/games/{game_id}"),
        ("GET", "/v1/games/{game_id}/materials"),
        ("GET", "/v1/games/{game_id}/materials/{material_key}"),
        ("GET", "/v1/games/{game_id}/evidence-assets/{evidence_id}"),
        ("GET", "/v1/games/{game_id}/findings"),
        ("GET", "/v1/games/{game_id}/views/{screen}"),
        ("POST", "/v1/games/{game_id}/examinations"),
        ("POST", "/v1/games/{game_id}/interrogations"),
        ("POST", "/v1/games/{game_id}/inferences"),
        ("POST", "/v1/games/{game_id}/phase-transitions"),
        ("PUT", "/v1/games/{game_id}/notes"),
        ("POST", "/v1/games/{game_id}/accusations"),
    }
    assert actual == expected
