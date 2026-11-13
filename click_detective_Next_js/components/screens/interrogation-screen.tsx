import { getInterviewTopics } from '@/lib/interview-topics';
import { ArrowRight, AudioLines, ChevronRight, Plus, LoaderCircle } from 'lucide-react';
import { evidence, suspects, questionLimit, type GameState } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';

type Props = Omit<
  Pick<
    CaseGameController,
    | 'state'
    | 'suspect'
    | 'setSuspect'
    | 'currentSuspect'
    | 'busy'
    | 'scrollEnd'
    | 'attachment'
    | 'setAttachment'
    | 'topicId'
    | 'setTopicId'
    | 'question'
    | 'setQuestion'
    | 'submitQuestion'
  >,
  'state'
> & { state: GameState };

export function InterrogationScreen({
  state,
  suspect,
  setSuspect,
  currentSuspect,
  busy,
  scrollEnd,
  attachment,
  setAttachment,
  question,
  setQuestion,
  topicId,
  setTopicId,
  submitQuestion,
}: Props) {
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">INTERROGATION ROOM</div>
        <h1>
          진술의 빈틈을 찾으세요<span>.</span>
        </h1>
        <p>
          이름·동선·목격 사실·증거를 물어보세요. FastAPI에서 생성하고 검증한 대사를 받습니다.{' '}
          <span className="subtle">FastAPI 연결</span>
        </p>
      </div>
      <div className="interrogation-grid">
        <div className="suspect-list">
          <div className="suspect-bio">
            <img
              className="suspect-portrait"
              src={currentSuspect.portrait}
              alt={`${currentSuspect.name} 인물 사진`}
              width={360}
              height={480}
            />
            <div className="eyebrow">PERSON OF INTEREST</div>
            <h3>{currentSuspect.name}</h3>
            <p>
              {currentSuspect.age}세 · {currentSuspect.bio}
            </p>
          </div>
          {suspects.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setSuspect(s.id);
                setTopicId('');
                setQuestion('');
              }}
              className={suspect === s.id ? 'selected' : ''}
            >
              <div className="avatar" style={{ background: s.color }}>
                <img
                  src={s.portrait}
                  alt={`${s.name} 인물 사진`}
                  width={72}
                  height={96}
                />
              </div>
              <div>
                <strong>{s.name}</strong>
                <span>{s.role}</span>
              </div>
              <ChevronRight size={14} />
            </button>
          ))}
        </div>
        <div className="chat">
          <div className="chat-heading">
            <span className="live-dot" />
            <strong>{currentSuspect.name}</strong>
            <span>진술 녹취록</span>
            <AudioLines size={19} />
          </div>
          <div className="messages" aria-live="polite">
            <div className="transcript-divider">INTERVIEW RECORD · CASE #0001</div>
            <div className="message suspect">
              <span>{currentSuspect.name} · 최초 진술</span>
              <p>{currentSuspect.statement}</p>
            </div>
            {state.messages
              .filter((m) => m.suspectId === suspect)
              .map((m, i) => (
                <div className={'message ' + m.role} key={i}>
                  <span>
                    {m.role === 'user' ? '수사관' : currentSuspect.name}
                    {m.evidenceId && ' · 증거 제시'}
                  </span>
                  <p>{m.text}</p>
                </div>
              ))}
            {busy && (
              <div className="typing">
                <LoaderCircle size={14} className="spin" /> 진술을 기록하고 있습니다…
              </div>
            )}
            <div ref={scrollEnd} />
          </div>
          <form className="composer" onSubmit={submitQuestion}>
            <div className="interview-topics" role="group" aria-label="심문 주제">
              <span>동선 · 다른 사람에 대해</span>
              {getInterviewTopics(suspect).map((topic) => (
                <button
                  key={topic.id}
                  type="button"
                  aria-pressed={topicId === topic.id}
                  disabled={busy || !!state.verdict || state.questions >= questionLimit}
                  onClick={() => {
                    setQuestion(topic.question);
                    setTopicId(topic.id);
                  }}
                >
                  {topic.label}
                </button>
              ))}
            </div>
            <label className="attachment">
              <Plus size={14} />
              <select
                aria-label="제시할 증거"
                value={attachment}
                disabled={busy || !!state.verdict}
                onChange={(e) => setAttachment(e.target.value)}
              >
                <option value="">증거 첨부하기</option>
                {Object.values(state.derivedEvidence).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.code} · {item.title}
                  </option>
                ))}
                {evidence
                  .filter((e) => state.examined.includes(e.id))
                  .map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.code} · {e.title}
                    </option>
                  ))}
              </select>
            </label>
            <label className="sr-only" htmlFor="question">
              용의자에게 질문
            </label>
            <textarea
              id="question"
              rows={3}
              value={question}
              maxLength={1000}
              onChange={(e) => {
                setQuestion(e.target.value);
                setTopicId('');
              }}
              placeholder="그날 밤, 어디에 있었습니까?"
              disabled={busy || !!state.verdict || state.questions >= questionLimit}
            />
            <div className="composer-bottom">
              <span>
                {question.length}/1,000 <i /> 전체 남은 질문{' '}
                {questionLimit - state.questions}회
              </span>
              <button
                className="primary small"
                disabled={
                  busy ||
                  !question.trim() ||
                  !!state.verdict ||
                  state.questions >= questionLimit
                }
              >
                질문하기 <ArrowRight size={15} />
              </button>
            </div>
            {(state.verdict || state.questions >= questionLimit) && (
              <p className="quota-note">
                심문이 종료되었습니다. 증거와 타임라인을 검토하고{' '}
                {state.verdict ? '결과를 확인' : '고발을 진행'}하세요.
              </p>
            )}
          </form>
        </div>
      </div>
    </>
  );
}
