export interface LoanApplicationData {
  LOAN: number;
  MORTDUE: number;
  VALUE: number;
  REASON: "HomeImp" | "DebtCon" | "Other";
  JOB: "ProfExe" | "Mgr" | "Office" | "Sales" | "Self" | "Other";
  YOJ: number;
  DEROG: number;
  DELINQ: number;
  CLAGE: number;
  NINQ: number;
  CLNO: number;
  DEBTINC: number;
}

export type LimeExplanationType = Array<[string, number]>;
