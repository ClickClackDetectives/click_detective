import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

/** 같은 단위의 측정값을 가로 막대로 표시한다.
 * @param props 차트의 지표와 값.
 * @param props.label 지표 이름.
 * @param props.values 그룹별 측정값.
 * @param props.unit 측정 단위.
 * @returns 측정값 막대그래프.
 */
export function Bars({
  label,
  values,
  unit,
}: {
  label: string;
  values: { name: string; value: number | null; count: number }[];
  unit: string;
}) {
  const measured = values.filter((row) => row.value !== null);
  return (
    <div>
      <h4>{label}</h4>
      {measured.length > 0 && (
        <ResponsiveContainer width="100%" height={measured.length * 34 + 34} minWidth={0}>
          <BarChart data={measured} layout="vertical" margin={{ right: 22, left: 4 }}>
            <CartesianGrid horizontal={false} stroke="#48534a" />
            <XAxis
              type="number"
              domain={[0, unit === '%' ? 100 : 'auto']}
              unit={unit}
              tick={{ fill: '#d6d5c6', fontSize: 11 }}
            />
            <YAxis
              dataKey="name"
              type="category"
              width={112}
              tick={{ fill: '#d6d5c6', fontSize: 11 }}
              tickFormatter={(name: string) => (name.length > 12 ? name.slice(0, 11) + '…' : name)}
            />
            <Tooltip
              contentStyle={{ background: '#20241e', borderColor: '#777c62' }}
              labelStyle={{ color: '#f1eee6' }}
              itemStyle={{ color: '#f1eee6' }}
              cursor={{ fill: '#30392e' }}
            />
            <Bar
              dataKey="value"
              name={label}
              unit={unit}
              fill="#83c8a5"
              radius={[0, 4, 4, 0]}
              maxBarSize={15}
              isAnimationActive={false}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
      <ul className="agent-model-values">
        {values.map(({ name, value, count }) => (
          <li key={name}>
            {name} ·{' '}
            {value === null
              ? '미기록'
              : value.toLocaleString('ko-KR', { maximumFractionDigits: 1 }) + unit}{' '}
            · 표본 {count}건
          </li>
        ))}
      </ul>
    </div>
  );
}
