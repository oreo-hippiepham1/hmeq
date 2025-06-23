"use client"

import type React from "react"
import { useState } from "react"
import type { LoanApplicationData } from "../types"

interface InputFormProps {
  onSubmit: (data: LoanApplicationData, pipeline: string) => void
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<LoanApplicationData>({
    LOAN: 0,
    MORTDUE: 0,
    VALUE: 0,
    REASON: "HomeImp",
    JOB: "ProfExe",
    YOJ: 0,
    DEROG: 0,
    DELINQ: 0,
    CLAGE: 0,
    NINQ: 0,
    CLNO: 0,
    DEBTINC: 0,
  })

  const [pipeline, setPipeline] = useState<string>("rf")

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target

    // Convert numeric fields to numbers
    const numericFields = ["LOAN", "MORTDUE", "VALUE", "YOJ", "DEROG", "DELINQ", "CLAGE", "NINQ", "CLNO", "DEBTINC"]
    const newValue = numericFields.includes(name) ? Number.parseFloat(value) || 0 : value

    setFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData, pipeline)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Loan Amount
              <input
                type="number"
                name="LOAN"
                value={formData.LOAN}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Mortgage Due
              <input
                type="number"
                name="MORTDUE"
                value={formData.MORTDUE}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Property Value
              <input
                type="number"
                name="VALUE"
                value={formData.VALUE}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Reason
              <select
                name="REASON"
                value={formData.REASON}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              >
                <option value="HomeImp">Home Improvement</option>
                <option value="DebtCon">Debt Consolidation</option>
                <option value="Other">Other</option>
              </select>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Job
              <select
                name="JOB"
                value={formData.JOB}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              >
                <option value="ProfExe">Professional/Executive</option>
                <option value="Mgr">Manager</option>
                <option value="Office">Office</option>
                <option value="Sales">Sales</option>
                <option value="Self">Self-Employed</option>
                <option value="Other">Other</option>
              </select>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Years on Job
              <input
                type="number"
                name="YOJ"
                value={formData.YOJ}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Derogatory Reports
              <input
                type="number"
                name="DEROG"
                value={formData.DEROG}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Delinquent Accounts
              <input
                type="number"
                name="DELINQ"
                value={formData.DELINQ}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Age of Oldest Credit Line (months)
              <input
                type="number"
                name="CLAGE"
                value={formData.CLAGE}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Recent Credit Inquiries
              <input
                type="number"
                name="NINQ"
                value={formData.NINQ}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Number of Credit Lines
              <input
                type="number"
                name="CLNO"
                value={formData.CLNO}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Debt-to-Income Ratio
              <input
                type="number"
                name="DEBTINC"
                value={formData.DEBTINC}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
                required
              />
            </label>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 pt-4">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Model Pipeline
            <select
              value={pipeline}
              onChange={(e) => setPipeline(e.target.value)}
              className="mt-1 block w-full rounded-md border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 bg-white text-slate-900 p-2 border"
              required
            >
              <option value="dt">Decision Tree</option>
              <option value="rf">Random Forest</option>
              <option value="knn">K-Nearest Neighbors (will not have probability)</option>
              <option value="gb">Gradient Boosting</option>
              {/* <option value="svm">Support Vector Machine</option> */}
            </select>
          </label>
        </div>

        <div>
          <button
            type="submit"
            className="w-full md:w-auto px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm transition-colors"
          >
            Submit Application
          </button>
        </div>
      </div>
    </form>
  )
}

export default InputForm
