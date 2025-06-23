import type React from "react"
interface AgentAdviceProps {
  advice: {
    agent_interpretation: string
    financial_advice: string
  }
}

const AgentAdvice: React.FC<AgentAdviceProps> = ({ advice }) => {
  return (
    <div className="mt-6 space-y-4">
      <h3 className="text-lg font-semibold text-slate-800">AI Agent Analysis</h3>

      <div className="bg-slate-50 p-5 rounded-lg border border-slate-200">
        <div className="flex items-center mb-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-blue-600 mr-2"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9z"
              clipRule="evenodd"
            />
          </svg>
          <h4 className="font-medium text-blue-800">Interpretation</h4>
        </div>
        <p className="text-slate-700 whitespace-pre-line">{advice.agent_interpretation}</p>
      </div>

      <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
        <div className="flex items-center mb-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-blue-600 mr-2"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
            <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
          </svg>
          <h4 className="font-medium text-blue-800">Financial Advice</h4>
        </div>
        <p className="text-blue-700 whitespace-pre-line">{advice.financial_advice}</p>
      </div>
    </div>
  )
}

export default AgentAdvice
