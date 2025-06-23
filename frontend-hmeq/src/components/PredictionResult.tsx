import type React from "react"
interface PredictionResultProps {
  probability: number
}

const PredictionResult: React.FC<PredictionResultProps> = ({ probability }) => {
  // Format probability as percentage
  const formattedProbability = (probability * 100).toFixed(2)

  // Determine risk level based on probability
  let riskLevel = "Low"
  let colorClass = "text-green-600"
  let bgColorClass = "bg-green-50"
  let borderColorClass = "border-green-200"
  let progressColorClass = "bg-green-500"

  if (probability > 0.7) {
    riskLevel = "High"
    colorClass = "text-red-600"
    bgColorClass = "bg-red-50"
    borderColorClass = "border-red-200"
    progressColorClass = "bg-red-500"
  } else if (probability > 0.3) {
    riskLevel = "Medium"
    colorClass = "text-amber-600"
    bgColorClass = "bg-amber-50"
    borderColorClass = "border-amber-200"
    progressColorClass = "bg-amber-500"
  }

  return (
    <div className={`${bgColorClass} ${borderColorClass} border rounded-lg p-5`}>
      <h3 className="text-lg font-semibold mb-3 text-slate-800">Default Prediction Result</h3>

      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium text-slate-700">Probability of Default</span>
          <span className={`text-sm font-bold ${colorClass}`}>{formattedProbability}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div
            className={`h-2.5 rounded-full ${progressColorClass}`}
            style={{ width: `${Math.min(probability * 100, 100)}%` }}
          ></div>
        </div>
      </div>

      <div className="flex items-center">
        <div className={`w-3 h-3 rounded-full ${progressColorClass} mr-2`}></div>
        <span className="text-sm text-slate-700">Risk Level:</span>
        <span className={`ml-2 text-sm font-bold ${colorClass}`}>{riskLevel}</span>
      </div>
    </div>
  )
}

export default PredictionResult
