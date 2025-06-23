from pydantic import BaseModel, Field
from typing import Literal, List, Tuple

class LoanApplicationRequest(BaseModel):
    LOAN: float = Field(description="The loan amount")
    MORTDUE: float = Field(description="The mortgage due")
    VALUE: float = Field(description="The property value")
    REASON: Literal['HomeImp', 'DebtCon', 'Other'] = Field(description="The reason for the loan")
    JOB: Literal['ProfExe', 'Mgr', 'Office', 'Sales', 'Self', 'Other'] = Field(description="The job of the applicant")
    YOJ: float = Field(description="The years of experience on the job")
    DEROG: float = Field(description="The number of derogatory reports")
    DELINQ: float = Field(description="The number of delinquent accounts")
    CLAGE: float = Field(description="The average age of the credit lines")
    NINQ: float = Field(description="The number of recent credit inquiries")
    CLNO: float = Field(description="The number of credit lines")
    DEBTINC: float = Field(description="The debt-to-income ratio")

class AgentAdviceRequest(BaseModel):
    default_probability: float = Field(description="Probability of default", ge=0.0, le=1.0)
    lime_explanations: List[Tuple[str, float]] = Field(description="LIME explanations as a list of (feature_condition, weight) tuples")