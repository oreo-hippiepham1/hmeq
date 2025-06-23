"use client"

import { useState } from "react"
import InputForm from "./components/InputForm"
import PredictionResult from "./components/PredictionResult"
import LimeExplanation from "./components/LimeExplanation"
import AgentAdvice from "./components/AgentAdvice"
import type { LoanApplicationData, LimeExplanationType } from "./types"
import "./App.css"

function App() {
  const [loanData, setLoanData] = useState<LoanApplicationData | null>(null)
  const [selectedPipeline, setSelectedPipeline] = useState<string>("rf")
  const [defaultProbability, setDefaultProbability] = useState<number | null>(null)
  const [limeExplanation, setLimeExplanation] = useState<LimeExplanationType | null>(null)
  const [agentAdvice, setAgentAdvice] = useState<{
    agent_interpretation: string
    financial_advice: string
  } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleFormSubmit = (data: LoanApplicationData, pipeline: string) => {
    setLoanData(data)
    setSelectedPipeline(pipeline)
    setDefaultProbability(null)
    setLimeExplanation(null)
    setAgentAdvice(null)
    setError(null)
  }

  const handlePredict = async () => {
    if (!loanData) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/predict/${selectedPipeline}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loanData),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setDefaultProbability(data.probability_of_default)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  const handleExplain = async () => {
    if (!loanData) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/explain_custom_instance/${selectedPipeline}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(loanData),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setLimeExplanation(data.lime_explanation)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  const handleGetAdvice = async () => {
    if (defaultProbability === null || !limeExplanation) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch("http://localhost:8000/agent/advice", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          default_probability: defaultProbability,
          lime_explanations: limeExplanation,
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data = await response.json()
      setAgentAdvice(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">Loan Default Prediction</h1>
          <p className="text-slate-600">Analyze loan applications with machine learning and AI-driven insights</p>
        </header>

        <div className="grid gap-8">
          <div className="bg-white rounded-xl shadow-md p-6 border border-slate-100">
            <h2 className="section-title">Loan Application Details</h2>
            <InputForm onSubmit={handleFormSubmit} />
          </div>

          {loanData && (
            <div className="bg-white rounded-xl shadow-md p-6 border border-slate-100">
              <h2 className="section-title">Analysis</h2>

              <div className="flex flex-col gap-4">
                <div>
                  <button
                    onClick={handlePredict}
                    disabled={isLoading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
                  >
                    {isLoading && defaultProbability === null ? (
                      <>
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        Predicting...
                      </>
                    ) : (
                      "Predict Default Probability"
                    )}
                  </button>
                </div>

                {defaultProbability !== null && (
                  <>
                    <PredictionResult probability={defaultProbability} />

                    <div className="mt-2">
                      <button
                        onClick={handleExplain}
                        disabled={isLoading}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
                      >
                        {isLoading && !limeExplanation ? (
                          <>
                            <svg
                              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                            >
                              <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                              ></circle>
                              <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                              ></path>
                            </svg>
                            Generating Explanation...
                          </>
                        ) : (
                          "Explain Prediction"
                        )}
                      </button>
                    </div>
                  </>
                )}

                {limeExplanation && (
                  <>
                    <LimeExplanation explanation={limeExplanation} />

                    <div className="mt-2">
                      <button
                        onClick={handleGetAdvice}
                        disabled={isLoading}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-md shadow-sm transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
                      >
                        {isLoading && !agentAdvice ? (
                          <>
                            <svg
                              className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                            >
                              <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="currentColor"
                                strokeWidth="4"
                              ></circle>
                              <path
                                className="opacity-75"
                                fill="currentColor"
                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                              ></path>
                            </svg>
                            Getting Advice...
                          </>
                        ) : (
                          "Get AI Advice"
                        )}
                      </button>
                    </div>
                  </>
                )}

                {agentAdvice && <AgentAdvice advice={agentAdvice} />}

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4">
                    <div className="flex">
                      <svg
                        className="h-5 w-5 text-red-500 mr-2"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                          clipRule="evenodd"
                        />
                      </svg>
                      <p>
                        <strong>Error:</strong> {error}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
