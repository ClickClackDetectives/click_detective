/** 원본 문서 팝업에 전달하는 공통 형식. 실제 본문은 상세 API에서 읽습니다. */
export type InvestigationDocument = {
  id: string;
  code: string;
  kind: 'evidence' | 'derived' | 'testimony';
  title: string;
  type: string;
  body: string;
};
