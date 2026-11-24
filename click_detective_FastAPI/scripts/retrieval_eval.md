# 자유 질문 진술 검색 평가

이 평가는 《열세 번째 종》에서 자유 질문에 답할 진술을 찾을 수 있는지 검사한다. 질문과 진술 ID를 비교하므로 FastAPI 서버, Qwen, 생성된 대사가 필요하지 않다. 현재 서비스에서 전처리 LLM이 최종 진술을 선택하는 경로의 품질은 별도 평가 대상이다.

## 평가 데이터

`retrieval_eval_cases.json`에는 다섯 인물의 한국어 질문 42개가 있다. 같은 진술을 묻는 표현 변형은 한 그룹에 모았다. 각 그룹에는 인물 ID, 이미 공개된 쟁점, 기대 진술 ID를 적는다. `expected_fact_ids: []`는 해당 상태의 공개 동선에 질문에 답할 근거가 없다는 뜻이다.

- **기준 조정 13문항**은 점수 기준점을 선택하는 데 사용한다.
- **최종 평가 29문항**은 선택한 기준점을 적용한 결과를 보는 데 사용한다.
- 직접 질문, 돌려 말한 질문, 오타, 사건과 무관한 질문, 단어는 비슷하지만 정답 근거가 없는 질문을 포함한다.
- 다른 인물에게 묻는 경우와 동일한 질문을 증거 공개 전후에 묻는 경우를 포함한다. 공개 전후의 후보는 서버와 같은 `movement()` 함수로 구한다.

평가 범위는 공개 동선 진술과 그 동선에 포함되는 인정 진술이다. 각 문항을 독립 요청으로 보고 최근 대화는 사용하지 않는다. 모호한 질문의 정답은 현재 후보 기준으로 운영상 기대하는 진술 ID다.

## 실행

FastAPI 폴더에서 실행한다. 기본 실행은 현재 코드의 단어·문자 점수 함수를 사용한다. 검색 후보 텍스트는 현재 전처리와 같이 시각, 제목, 진술 원문을 합친다.

```powershell
python -m scripts.evaluate_retrieval --top-k 3 --output .reports/retrieval-lexical.json
```

임베딩을 비교할 때는 현재 Python 환경에 Sentence Transformers 5 이상을 설치하고, 모델 이름 또는 로컬 모델 경로를 지정한다. 아래 명령은 E5의 문서·질문 접두어를 지정하는 예다. 모델별 지침에 따라 접두어를 지정하면 된다. [E5 모델 카드](https://huggingface.co/intfloat/multilingual-e5-small#faq) · [Sentence Transformers 문서](https://sbert.net/docs/package_reference/sentence_transformer/model.html)

```powershell
python -m pip install "sentence-transformers>=5,<6" sentencepiece
python -m scripts.evaluate_retrieval --embedding-model intfloat/multilingual-e5-small --query-prefix "query: " --passage-prefix "passage: " --top-k 3 --output .reports/retrieval-comparison.json
```

표준 출력에는 요약과 질문 유형별 지표가 나온다. `--output` 보고서에는 각 최종 평가 질문의 후보 순위, 점수, 선택된 진술 ID와 기대 진술 ID가 들어간다.

## 평가지표

| 지표 | 보는 것 |
|---|---|
| **Hit@1** | 답할 근거가 있는 질문에서 첫 번째 후보가 정답인 비율 |
| **Recall@k** | 답할 근거가 있는 질문마다 상위 (k)건에 포함된 정답 진술의 비율을 계산한 뒤 평균 |
| **MRR@k** | 답할 근거가 있는 질문마다 첫 정답 순위의 역수 (1/순위)를 구한 뒤 평균. 상위 (k)건에 정답이 없으면 0점 |
| **선택 정밀도** | 점수 기준 적용 후 실제 선택한 진술 전체 중 정답 진술의 비율 |
| **정답 목록 일치율** | 답할 근거가 있는 질문에서 실제 선택한 진술 집합이 정답 집합과 정확히 같은 비율 |
| **근거 없는 질문의 오탐률** | 답할 근거가 없는 질문에서 진술을 한 건이라도 반환한 비율. 낮을수록 좋다 |

순위 지표는 관련성 기준을 적용하기 전 순위를 사용한다. 선택 지표는 기준을 통과한 최대 `top_k`건을 사용한다. 기준점을 결정할 때는 기준 조정 세트의 정답 목록 일치율과 근거 없는 질문의 거절률을 동일한 비중으로 계산한다. 모델마다 점수 범위가 달라 기준점은 모델별로 구한다. 순위 지표의 표준 구현은 [NIST trec_eval](https://github.com/usnistgov/trec_eval)에서 참고할 수 있다.
