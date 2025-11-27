from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional, List
from stock_analyzer import analyze_stocks
import os

app = FastAPI(
    title="Stock Analysis Tool",
    description="A tool to identify stocks that dropped significantly from YTD high and increased today",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


# Pydantic models for request/response validation
class AnalyzeRequest(BaseModel):
    drop_threshold: float = Field(default=0.40, ge=0, le=1, description="Minimum drop from year high (0.0 to 1.0)")
    increase_threshold: float = Field(default=0.05, ge=0, le=1, description="Minimum increase today (0.0 to 1.0)")
    max_stocks: Optional[int] = Field(default=None, ge=1, description="Maximum number of stocks to analyze")


class StockResult(BaseModel):
    ticker: str
    yesterday_price: float
    today_price: float
    ytd_high: float
    drop_from_high: float
    increase_today: float
    yesterday_date: str
    today_date: str
    full_year_data: bool
    data_start_date: str


class AnalyzeResponse(BaseModel):
    success: bool
    results: List[StockResult]
    count: int


class ErrorResponse(BaseModel):
    success: bool
    error: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/analyze", response_model=AnalyzeResponse, responses={500: {"model": ErrorResponse}})
async def analyze(request_data: AnalyzeRequest):
    """API endpoint to analyze stocks"""
    try:
        # Run analysis
        results = analyze_stocks(
            drop_threshold=request_data.drop_threshold,
            increase_threshold=request_data.increase_threshold,
            max_stocks=request_data.max_stocks
        )
        
        # Format results for JSON response
        formatted_results = []
        for stock in results:
            formatted_results.append(StockResult(
                ticker=stock['ticker'],
                yesterday_price=round(stock['yesterday_price'], 2),
                today_price=round(stock['today_price'], 2),
                ytd_high=round(stock['ytd_high'], 2),
                drop_from_high=round(stock['drop_from_high'] * 100, 2),
                increase_today=round(stock['increase_today'] * 100, 2),
                yesterday_date=str(stock['yesterday_date']),
                today_date=str(stock['today_date']),
                full_year_data=stock.get('full_year_data', True),
                data_start_date=str(stock.get('data_start_date', 'N/A'))
            ))
        
        return AnalyzeResponse(
            success=True,
            results=formatted_results,
            count=len(formatted_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
