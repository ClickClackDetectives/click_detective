# 기본 모델 위치

로컬 Qwen2.5-7B-Instruct 폴더를 이 위치에 복사하세요.

```text
models/Qwen2.5-7B-Instruct/
  config.json
  tokenizer_config.json
  tokenizer.json
  model.safetensors.index.json
  model-*.safetensors
```

실제 파일 구성은 모델에 따라 다릅니다. 서버는 로컬 파일만 읽고 NF4 4비트로 로딩합니다. .env의 CLICK_LOCAL_MODEL_PATH로 다른 경로를 지정할 수 있습니다.
