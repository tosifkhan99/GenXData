from typing import Dict, Any
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.strategy_mapping import get_all_strategy_names, get_all_strategy_schemas
from exceptions.param_exceptions import InvalidConfigParamException
from utils.ip_tracker import ip_tracker
from main import start
import tempfile
import zipfile
import pandas as pd
import os
from io import BytesIO
from datetime import datetime, timedelta

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Admin authentication
# ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'your-super-secret-admin-key-here')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')

async def verify_admin_key(x_api_key: str = Header(None)):
    """Verify admin API key from header"""
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing admin API key"
        )
    return True

origins = [
    "http://localhost:5173",
    "https://tosifkhan99.github.io",  # Add your GitHub Pages domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def catch_all_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        
        # Log the request for tracking
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Extract rows requested from request body if applicable
        rows_requested = 0
        if request.url.path in ['/generate_and_download', '/generate_data']:
            try:
                body = await request.body()
                if body:
                    import json
                    config = json.loads(body.decode())
                    rows_requested = config.get('num_of_rows', 0)
            except:
                pass
        
        ip_tracker.log_request(
            ip_address=client_ip,
            endpoint=request.url.path,
            rows_requested=rows_requested,
            user_agent=user_agent,
            status_code=response.status_code
        )
        
        return response
    except Exception as e:
        # Log the exception for debugging
        print(e)
        # Return a generic 500 error response
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected internal server error occurred."},
        )



@app.get('/ping')
@limiter.limit("100/minute") 
async def ping(request: Request):
    return {"message": "pong"}


@app.get('/get_all_strategies')
@limiter.limit("30/minute")  
async def get_all_strategies(request: Request):
    return {"strategies": get_all_strategy_names()}


@app.get('/get_strategy_schemas')
@limiter.limit("30/minute")  
async def get_strategy_schemas(request: Request):
    return {"strategies": get_all_strategy_schemas()}


@app.post('/generate_data')
@limiter.limit("5/minute") 
async def generate_data(request: Request, config: Dict[str, Any]):
    return {"data": start(config)}


@app.post('/generate_and_download')
@limiter.limit("3/minute")
async def generate_and_download(request: Request, config: Dict[str, Any]):
    """
    Generate data based on config and return as a zip file containing the generated files.
    """
    try:
        # Validate row count for demo mode
        num_rows = config.get('num_of_rows', 0)
        if num_rows > 5000:
            return JSONResponse(
                status_code=400,
                content={"error": "Row limit exceeded", "message": "Maximum 5,000 rows allowed in demo mode"}
            )
        if num_rows < 1:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid row count", "message": "Minimum 1 row required"}
            )
        # Force write_output to True to generate files
        config['write_output'] = True
        
        # Get the configured output file path and format
        file_writer = config.get('file_writer', [{}])[0]
        writer_type = file_writer.get('type', 'CSV_WRITER')
        output_path = file_writer.get('params', {}).get('output_path', '')
        
        # Ensure output directory exists
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate the data (this will create the output file)
        result = start(config)
        
        # Create a zip file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the generated file to the zip
            if output_path and os.path.exists(output_path):
                # Get the filename from the path
                filename = os.path.basename(output_path)
                zip_file.write(output_path, filename)
                
                # Clean up the temporary file
                os.remove(output_path)
            else:
                # Fallback: create file from the returned data
                df = pd.DataFrame(result.get('df', []))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                df.to_csv(temp_file.name, index=False)
                zip_file.write(temp_file.name, 'generated_data.csv')
                os.unlink(temp_file.name)
        
        zip_buffer.seek(0)
        
        # Get project name for filename
        project_name = config.get('metadata', {}).get('name', 'generated_data')
        filename = f"{project_name.replace(' ', '_')}_data.zip"
        
        # Return the zip file as a streaming response
        return StreamingResponse(
            BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate data", "message": str(e)}
        )


@app.post('/generate_config')
@limiter.limit("10/minute") 
async def generate_config(request: Request, config: Dict[str, Any]):
    return {"config": generate_config(config)}


@app.exception_handler(InvalidConfigParamException)
async def invalid_config_param_exception_handler(request: Request, exc: InvalidConfigParamException):
    return JSONResponse(
        status_code=400,
        content={"error_name": exc.name, "message": f"Oops! {exc.message}. We are on it!"},
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={"error_name": exc.name, "message": f"Something went wrong while generating data."},
    )


# Admin Dashboard Endpoints (protected)
@app.get('/admin/dashboard')
@limiter.limit("10/minute")
async def admin_dashboard(request: Request, admin: bool = Depends(verify_admin_key)):
    """Admin dashboard with usage statistics"""
    try:
        return {
            "top_users_24h": ip_tracker.get_top_users(hours=24, limit=10),
            "top_users_1h": ip_tracker.get_top_users(hours=1, limit=5),
            "total_requests_24h": len([
                usage for usage in ip_tracker.usage_data 
                if usage.timestamp > datetime.now() - timedelta(hours=24)
            ]),
            "total_rows_generated_24h": sum([
                usage.rows_requested for usage in ip_tracker.usage_data 
                if usage.timestamp > datetime.now() - timedelta(hours=24)
            ])
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to load dashboard data", "message": str(e)}
        )


@app.get('/admin/ip/{ip_address}')
@limiter.limit("20/minute")
async def get_ip_details(request: Request, ip_address: str, admin: bool = Depends(verify_admin_key)):
    """Get detailed information about a specific IP"""
    try:
        stats = ip_tracker.get_ip_stats(ip_address, hours=24)
        suspicious = ip_tracker.is_suspicious_activity(ip_address)
        
        return {
            "ip_address": ip_address,
            "stats": stats,
            "suspicious_activity": suspicious
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get IP details", "message": str(e)}
        )
