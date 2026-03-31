
import {
    CartesianGrid,
    Line,
    LineChart,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

function MetricGraph({ title, data, color = "#8884d8", transitionLines = [] }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow border">
      <h3 className="text-lg font-semibold mb-3 text-gray-800">{title}</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="temp" 
            reversed 
            hide={true}
          />
          <YAxis 
            label={{ value: title, angle: -90, position: "insideLeft" }}
          />
          <Tooltip 
            formatter={(value, name) => [value, name]}
            labelFormatter={(label) => `Temperature: ${label.toFixed(1)}°C`}
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '4px',
              padding: '8px'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke={color} 
            strokeWidth={1.5}
            dot={{ r: 2, fill: color, strokeWidth: 1, stroke: 'white' }}
            activeDot={{ r: 4, fill: color, strokeWidth: 2, stroke: 'white' }}
          />
          {transitionLines.map((t, i) => (
            <ReferenceLine key={i} x={t} stroke="red" strokeDasharray="5 5" strokeWidth={1} />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <div className="text-center mt-2">
        <span className="text-sm text-gray-500">Temperature (°C)</span>
      </div>
    </div>
  );
}

export default MetricGraph;