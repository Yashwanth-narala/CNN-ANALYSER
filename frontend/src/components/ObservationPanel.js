import { useState } from "react";
import MetricGraph from "./MetricGraph";

function ObservationPanel({ metrics, transitions }) {
  const [selectedMetric, setSelectedMetric] = useState("Mean");

  const metricNames = Object.keys(metrics).filter(m => m !== "Temperature" && m !== "Filename");
  const tempArray = metrics["Temperature"];

  const graphData = metricNames.map(metric => ({
    name: metric,
    data: tempArray.map((t, i) => ({ temp: t, value: metrics[metric][i] })),
  }));

  const selectedData = graphData.find(g => g.name === selectedMetric)?.data || [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg mb-6 border">
      <div className="mb-4">
        <label className="block mb-2 font-medium text-gray-700">Select Metric to Observe:</label>
        <select
          className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
        >
          {metricNames.map(name => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </div>

      <MetricGraph
        title={`Observation View: ${selectedMetric}`}
        data={selectedData}
        transitionLines={Object.values(transitions)}
      />
    </div>
  );
}

export default ObservationPanel;