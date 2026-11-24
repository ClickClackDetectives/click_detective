import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SweepPoint } from '@/app/game/rag-dashboard/metrics';

const lines = {
  first: { label: '관련 진술이 1위', color: '#c8a3ef' },
  complete: { label: '필요한 진술 모두 선택', color: '#76d2bf' },
  exact: { label: '필요한 진술만 선택', color: '#e6c276' },
  falseMatch: { label: '오탐', color: '#f2a199' },
} as const;

/** 선택한 설정에서 측정된 성능 곡선을 표시한다.
 * @param props 차트의 측정값, 선택한 설정과 표시할 지표.
 * @param props.points 선택한 보조 설정에 대응하는 측정 결과.
 * @param props.selected 사용자가 선택한 기본 설정의 값.
 * @param props.weights 가중치 실험이면 가로축을 백분율로 표시하는지 여부.
 * @returns 설정별 측정값을 그린 차트와 지표 범례.
 */
export function SweepChart({
  points,
  selected,
  weights,
}: {
  points: SweepPoint[];
  selected: number;
  weights: boolean;
}) {
  const visible = weights
    ? (['first', 'complete', 'exact'] as const)
    : (['complete', 'exact', 'falseMatch'] as const);
  /** 가로축과 도구 설명에 표시할 설정값을 포맷한다.
   * @param value 임계값 또는 0과 1 사이의 E5 가중치.
   * @returns 현재 실험에 맞는 읽기 쉬운 설정값.
   */
  function formatSetting(value: number) {
    return weights ? `${Math.round(value * 100)}%` : String(value);
  }

  return (
    <figure className="rag-chart">
      <div className="rag-plot" aria-hidden="true">
        <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 680, height: 260 }}>
          <LineChart data={points} margin={{ top: 12, right: 15, left: 0, bottom: 6 }}>
            <CartesianGrid vertical={false} stroke="#394843" strokeDasharray="3 4" />
            <XAxis
              dataKey="setting"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={formatSetting}
              tick={{ fill: '#b4c5bd', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 100]}
              tickFormatter={(value) => value + '%'}
              tick={{ fill: '#b4c5bd', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              width={45}
            />
            <Tooltip
              labelFormatter={(value) => formatSetting(Number(value))}
              formatter={(value) => Number(value).toFixed(1) + '%'}
              contentStyle={{ background: '#192420', borderColor: '#566961', borderRadius: '8px' }}
              labelStyle={{ color: '#f4f0e5' }}
            />
            <ReferenceLine x={selected} stroke="#a9b7af" strokeDasharray="5 4" />
            {visible.map((key) => (
              <Line
                key={key}
                dataKey={key}
                name={lines[key].label}
                stroke={lines[key].color}
                strokeWidth={2.3}
                type="stepAfter"
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <figcaption>
        <span>{weights ? '가로축은 E5 가중치' : '가로축은 최소 유사도'}</span>
        <ul className="rag-legend" aria-label="그래프 지표">
          {visible.map((key) => (
            <li key={key}>
              <span className="rag-swatch" style={{ background: lines[key].color }} />
              {lines[key].label}
            </li>
          ))}
        </ul>
      </figcaption>
    </figure>
  );
}
