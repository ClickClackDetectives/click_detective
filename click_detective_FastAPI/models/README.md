# 로컬 모델 파일 준비

FastAPI는 local 모드에서 디스크에 준비한 Qwen 모델을 NF4 4비트로 로딩합니다. 모델 폴더에는 설정, 토크나이저, 가중치 및 가중치가 분할된 경우 인덱스 파일을 함께 둡니다.

| 용도 | 설정과 파일 |
| --- | --- |
| 대사 생성과 의미 검증 | `CLICK_LOCAL_MODEL_PATH`가 가리키는 Qwen 폴더. 기본 위치는 `models/Qwen2.5-7B-Instruct/` |
| 학습된 LoRA 적용 | `CLICK_LORA_ADAPTER_PATH`가 가리키는 호환 어댑터 폴더. 기본 위치는 `adapters/best_adapter/` |
| 자유 질문 검색 | `CLICK_RAG_EMBEDDING_DIR`에 `e5.onnx`와 같은 모델의 `tokenizer.json` 배치. local 기본 위치는 `models/retrieval/` |
| 검증 문장 유사도 | `CLICK_VALIDATION_EMBEDDING_MODEL`에 미리 준비한 SentenceTransformer 경로 또는 캐시에 있는 모델 ID 지정 |

E5에 사용할 파일은 multilingual-e5-small의 ONNX 모델이며, 기존 AVX-512 VNNI용 구성은 `model_qint8_avx512_vnni.onnx`를 `e5.onnx`로 저장합니다. 설치와 의존성은 [FastAPI 실행 안내](../README.md), 검색과 검증의 사용 위치는 [에이전트 문서](../docs/에이전트/README.md)에서 확인합니다.
