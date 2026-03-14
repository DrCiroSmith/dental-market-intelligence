from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Ensure Python can find our local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from valuation_models.ebitda_multiples import PracticeValuationModel
from data_pipeline.demographics_etl import DemographicsETL

app = FastAPI(title="Dental Market Intelligence API", version="1.0.0")

# Initialize our engines
valuation_engine = PracticeValuationModel()
etl_engine = DemographicsETL()

class ValuationRequest(BaseModel):
    net_income: float
    interest: float
    taxes: float
    depreciation: float
    add_backs: float
    practice_type: str = 'solo_gp'

@app.post("/api/v1/valuate")
def get_valuation(req: ValuationRequest):
    """
    Receives raw financials, calculates Adjusted EBITDA, and returns the multiple spread.
    """
    try:
        adj_ebitda = valuation_engine.calculate_adjusted_ebitda(
            req.net_income, req.interest, req.taxes, req.depreciation, req.add_backs
        )
        valuation = valuation_engine.baseline_valuation(adj_ebitda, req.practice_type)
        
        return {
            "status": "success",
            "practice_type": req.practice_type,
            "adjusted_ebitda": adj_ebitda,
            "valuation_range": valuation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "operational", "engines": ["valuation", "etl"]}
