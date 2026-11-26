"""CPU에서 multilingual E5로 질문과 진술을 벡터화한다."""


class E5Encoder:
    """평가에 사용한 multilingual-e5-small ONNX 모델을 로드한다.

    Args:
        directory: e5.onnx와 tokenizer.json을 담은 디렉터리.
    Returns:
        E5Encoder: 서버가 공유할 문장 임베딩 모델.
    """

    def __init__(self, directory):
        """모델과 토크나이저를 시작 시 한 번 준비한다.

        Args:
            directory: 모델과 토크나이저의 저장 위치.
        Returns:
            None: CPU 추론 세션을 초기화한다.
        """
        model_path = directory / "e5.onnx"
        tokenizer_path = directory / "tokenizer.json"
        if not model_path.is_file() or not tokenizer_path.is_file():
            raise RuntimeError(f"E5 requires e5.onnx and tokenizer.json in {directory}")

        import numpy as np
        import onnxruntime as ort
        from tokenizers import Tokenizer

        self.np = np
        self.tokenizer = Tokenizer.from_file(str(tokenizer_path))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(
            pad_id=self.tokenizer.token_to_id("<pad>"), pad_token="<pad>"
        )
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(
            str(model_path), sess_options=options, providers=["CPUExecutionProvider"]
        )
        self.inputs = [item.name for item in self.session.get_inputs()]

    def encode(self, texts, *, prefix):
        """패딩을 제외한 토큰 평균을 구하고 L2 정규화한다.

        Args:
            texts: 같은 용도의 질문 또는 진술 텍스트.
            prefix: E5의 query: 또는 passage: 접두어.
        Returns:
            ndarray: 텍스트 순서와 일치하는 단위 벡터 배열.
        """
        np = self.np
        tokens = self.tokenizer.encode_batch([prefix + text for text in texts])
        payload = {
            "input_ids": np.array([token.ids for token in tokens], dtype=np.int64),
            "attention_mask": np.array(
                [token.attention_mask for token in tokens], dtype=np.int64
            ),
            "token_type_ids": np.array(
                [token.type_ids for token in tokens], dtype=np.int64
            ),
        }
        (hidden,) = self.session.run(
            ["last_hidden_state"], {name: payload[name] for name in self.inputs}
        )
        mask = payload["attention_mask"][..., None].astype(hidden.dtype)
        pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1)
        norms = np.linalg.norm(pooled, axis=1, keepdims=True)
        if not np.isfinite(norms).all() or (norms == 0).any():
            raise ValueError("E5 produced an invalid embedding")
        return pooled / norms
