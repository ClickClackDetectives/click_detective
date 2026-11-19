import {
  percentile,
  stageTime,
  stageNames,
  type Run,
  type Stage,
} from '@/app/game/agent-dashboard/metrics';
import { summarize, time } from '@/app/game/agent-dashboard/summary';

const stages = Object.keys(stageNames) as Stage[];

/** 버전별 기록을 표로 비교한다.
 * @param props 비교 조건.
 * @param props.runs 선택한 모드의 실행 기록.
 * @param props.demo 예시 여부.
 * @returns 비교 표.
 */
export function Comparison({ runs: visible, demo }: { runs: Run[]; demo: boolean }) {
  const versions = [...new Set(visible.map((item) => item.version))];
  return (
    <section aria-labelledby="comparison-title">
      <h2 id="comparison-title">{demo ? '같은 질문의 개선 전후 예시' : '버전별 측정값 비교'}</h2>
      <p>
        {demo
          ? '가상의 질문·수치로 비교 방식을 보여줍니다.'
          : '동일한 질문과 수사 상태로 짝지은 실험은 별도로 진행해야 개선 효과를 판단할 수 있습니다.'}
      </p>
      <div className="agent-table">
        <table>
          <thead>
            <tr>
              <th>버전</th>
              <th>건수</th>
              <th>첫 후보 통과</th>
              <th>복구율</th>
              {stages.map((key) => (
                <th key={key}>{stageNames[key]}</th>
              ))}
              <th>전체 중앙값</th>
            </tr>
          </thead>
          <tbody>
            {versions.map((version) => {
              const items = visible.filter((item) => item.version === version);
              const values = summarize(items);
              return (
                <tr key={version}>
                  <th scope="row">{version}</th>
                  <td>{items.length}</td>
                  <td>{values.first}</td>
                  <td>{values.fallback}</td>
                  {stages.map((key) => (
                    <td key={key}>
                      {time(
                        percentile(
                          items.map((item) => stageTime(item, key)),
                          0.5,
                        ),
                      )}
                    </td>
                  ))}
                  <td>{values.median}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
