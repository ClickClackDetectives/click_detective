import {
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { percentile, type Run } from '@/app/game/agent-dashboard/metrics';

const colors = ['#83c8a5', '#84baf1', '#b5a6e8', '#e8bb71', '#c8cdb6', '#ef938a'];
const tooltipStyle = { background: '#20241e', borderColor: '#777c62', color: '#f1eee6' };

/** 실행 결과의 비율과 실제 건수를 표시한다.
 * @param props 결과 분류별 집계.
 * @param props.counts 분류명과 건수.
 * @returns 도넛 그래프와 범례.
 */
export function OutcomeChart({ counts }: { counts: { label: string; count: number }[] }) {
  const total = counts.reduce((sum, row) => sum + row.count, 0);
  const data = counts.map((row, index) => ({ ...row, fill: colors[index] }));
  return (
    <figure className="agent-donut">
      <div className="agent-donut-chart" role="group" aria-label="심문 결과 분포">
        <ResponsiveContainer width="100%" height={180} minWidth={0}>
          <PieChart>
            <Pie
              data={data.filter((row) => row.count > 0)}
              dataKey="count"
              nameKey="label"
              innerRadius="61%"
              outerRadius="88%"
              stroke="none"
              isAnimationActive={false}
            />
            <Tooltip contentStyle={tooltipStyle} itemStyle={{ color: '#f1eee6' }} />
          </PieChart>
        </ResponsiveContainer>
        <strong className="agent-donut-total">{total}건</strong>
      </div>
      <figcaption>
        <ul className="agent-legend">
          {data.map(({ label, count, fill }) => (
            <li key={label}>
              <span className="agent-dot" style={{ backgroundColor: fill }} />
              <span>{label}</span>
              <strong>
                {count}건 · {total ? Math.round((count / total) * 100) : 0}%
              </strong>
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
}

/** 모델별 응답 시간의 중앙값과 p95를 비교한다.
 * @param props 화면에 표시할 실행.
 * @param props.runs 현재 실행 모드의 목록.
 * @returns 모델별 응답 시간 그래프.
 */
export function ModelResponseChart({ runs }: { runs: Run[] }) {
  const groups = new Map<string, number[]>();
  for (const run of runs) {
    if (!run.experiment?.model || run.elapsed === null) continue;
    const model = run.experiment.model;
    const values = groups.get(model) ?? [];
    values.push(run.elapsed);
    groups.set(model, values);
  }
  const data = [...groups]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([model, values]) => ({
      model,
      median: percentile(values, 0.5),
      p95: percentile(values, 0.95),
      count: values.length,
    }));
  return (
    <section aria-labelledby="trend-title">
      <h2 id="trend-title">모델별 응답 시간</h2>
      <p>
        같은 실행 모드에서 모델별 전체 응답 시간을 비교합니다. 모델 이름은 가나다·알파벳 순입니다.
      </p>
      {data.length ? (
        <figure className="agent-trend">
          <ResponsiveContainer width="100%" height={250} minWidth={0}>
            <LineChart data={data} margin={{ top: 12, right: 16, left: 4, bottom: 8 }}>
              <CartesianGrid vertical={false} stroke="#48534a" />
              <XAxis
                dataKey="model"
                tick={{ fill: '#d6d5c6', fontSize: 12 }}
                tickFormatter={(model: string) =>
                  model.length > 14 ? model.slice(0, 13) + '…' : model
                }
              />
              <YAxis domain={[0, 'auto']} width={58} tick={{ fill: '#d6d5c6', fontSize: 12 }} />
              <Tooltip
                contentStyle={tooltipStyle}
                itemStyle={{ color: '#f1eee6' }}
                labelFormatter={(model) => {
                  const count = data.find((row) => row.model === model)?.count ?? 0;
                  return model + ' · ' + count + '건';
                }}
              />
              <Line
                dataKey="median"
                name="중앙값 (ms)"
                stroke={colors[0]}
                strokeWidth={2}
                isAnimationActive={false}
              />
              <Line
                dataKey="p95"
                name="p95 (ms)"
                stroke={colors[1]}
                strokeWidth={2}
                strokeDasharray="5 4"
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
          <figcaption>초록 실선 · 중앙값 / 파랑 점선 · p95 · 단위 ms</figcaption>
          <ul className="agent-model-values">
            {data.map(({ model, median, p95, count }) => (
              <li key={model}>
                <strong>{model}</strong> · {count}건 · 중앙값 {median} ms · p95 {p95} ms
              </li>
            ))}
          </ul>
        </figure>
      ) : (
        <p>모델 이름과 응답 시간이 함께 기록된 실행이 없습니다.</p>
      )}
    </section>
  );
}
