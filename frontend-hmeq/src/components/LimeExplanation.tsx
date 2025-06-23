import type React from "react"
import type { LimeExplanationType } from "../types"

interface LimeExplanationProps {
  explanation: LimeExplanationType
}

const LimeExplanation: React.FC<LimeExplanationProps> = ({ explanation }) => {
  // Sort explanations by absolute weight (most important first)
  const sortedExplanations = [...explanation].sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))

  return (
    <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
      <h3 className="text-lg font-semibold mb-2 text-slate-800">LIME Explanation</h3>
      <p className="text-sm text-slate-600 mb-4">
        These factors influenced the prediction (positive values increase default risk, negative values decrease it):
      </p>

      <div className="space-y-3">
        {sortedExplanations.map((item, index) => {
          const [feature, weight] = item
          const isPositive = weight > 0
          const barWidth = `${Math.min(Math.abs(weight) * 100, 100)}%`

          // Determine color based on whether it increases or decreases risk
          const barColor = isPositive ? "bg-red-500" : "bg-green-500"
          const textColor = isPositive ? "text-red-600" : "text-green-600"

          return (
            <div key={index} className="bg-white p-3 rounded-md shadow-sm">
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-slate-700">{feature}</span>
                <span className={`text-sm font-medium ${textColor}`}>
                  {weight > 0 ? "+" : ""}
                  {weight.toFixed(4)}
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${barColor}`}
                  style={{
                    width: barWidth,
                    marginLeft: isPositive ? "0" : "auto",
                  }}
                ></div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default LimeExplanation
