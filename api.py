from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.strategy_mapping import get_all_strategy_names, get_all_strategy_schemas
from exceptions.param_exceptions import InvalidConfigParamException
from main import start
import tempfile
import zipfile
import pandas as pd
import os
from io import BytesIO
from core.orchestrator import DataOrchestrator
from utils.generator_utils import (
    load_all_generators,
    list_available_generators,
    get_generator_info,
    get_generators_by_strategy,
    generator_to_config,
    get_generator_stats,
    validate_generator_config
)
from utils.logging import Logger

# Initialize API logger
logger = Logger.get_logger("api")

app = FastAPI(
    title="Data Generator API",
    description="Synthetic data generation API with 13+ strategies",
    version="1.0.0"
)

# Mount static files (for serving the React frontend)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    # Mount the assets directory at /assets path to match frontend expectations
    assets_path = os.path.join(static_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Mount static files for other assets like vite.svg, favicon.ico, etc.
    app.mount("/static", StaticFiles(directory=static_path), name="static")

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "*"  # Allow all origins for demo
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
        return await call_next(request)
    except Exception as e:
        # Log the exception for debugging
        logger.error(f"API Error: {e}", exc_info=True)
        # Return a generic 500 error response
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected internal server error occurred."},
        )

@app.get('/ping')
async def ping():
    return {"message": "pong", "status": "healthy"}

@app.get('/')
async def serve_frontend():
    """Serve the React frontend"""
    static_path = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Data Generator API", "status": "Frontend not built"}

@app.get('/{filename:path}')
async def serve_static_files(filename: str):
    """Serve static files like vite.svg, favicon.ico, etc. from root"""
    # Only serve specific file types to avoid conflicts with API routes
    allowed_extensions = {'.svg', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.txt', '.xml'}
    
    # Check if the filename has an allowed extension
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=404, detail="Not found")
    
    static_path = os.path.join(os.path.dirname(__file__), "static")
    file_path = os.path.join(static_path, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail="File not found")

@app.get('/get_all_strategies')
async def get_all_strategies():
    return {"strategies": get_all_strategy_names()}

@app.get('/get_strategy_schemas')
async def get_strategy_schemas():
    return {"strategies": get_all_strategy_schemas()}

@app.post('/generate_data')
async def generate_data(config: Dict[str, Any]):
    return {"data": start(config)}

@app.post('/generate_and_download')
async def generate_and_download(config: Dict[str, Any]):
    """
    Generate data based on config and return as a zip file containing the generated files.
    """
    try:
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

@app.get('/api/generators')
async def list_generators_api(filter_by: str = None):
    """List available generators with optional filtering."""
    try:
        generators = list_available_generators(filter_by)
        
        return {
            "generators": generators,
            "count": len(generators),
            "filter": filter_by
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/generators/{generator_name}')
async def get_generator_api(generator_name: str):
    """Get detailed information about a specific generator."""
    try:
        generator_info = get_generator_info(generator_name)
        
        return {
            "name": generator_name,
            "generator": generator_info
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/generators/by-strategy/{strategy_name}')
async def get_generators_by_strategy_api(strategy_name: str):
    """Get generators using a specific strategy."""
    try:
        generators = get_generators_by_strategy(strategy_name)
        
        return {
            "strategy": strategy_name,
            "generators": generators,
            "count": len(generators)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/generators/stats')
async def get_generator_stats_api():
    """Get generator statistics."""
    try:
        stats = get_generator_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/config/from-generators')
async def create_config_from_generators_api(data: dict):
    """Create a configuration from generator mappings."""
    try:        
        generator_mapping = data.get('mapping')
        if not generator_mapping:
            raise HTTPException(status_code=400, detail="No generator mapping provided")
        
        num_rows = data.get('num_rows', 100)
        metadata = data.get('metadata', {})
        output_config = data.get('output_config')
        
        # Create configuration
        config = generator_to_config(
            generator_mapping,
            num_rows=num_rows,
            output_config=output_config,
            metadata=metadata
        )
        
        # Validate configuration
        validate_generator_config(config)
        
        return {
            "status": "success",
            "config": config
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/config/validate')
async def validate_config_api(config: dict):
    """Validate a configuration."""
    try:
        # Validate configuration
        is_valid = validate_generator_config(config)
        
        return {
            "valid": is_valid,
            "message": "Configuration is valid"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/api/schemas/config')
async def get_config_schema_api():
    """Get the configuration schema documentation."""
    schema = {
        "type": "object",
        "required": ["column_name", "num_of_rows", "configs"],
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "version": {"type": "string"}
                }
            },
            "column_name": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of column names"
            },
            "num_of_rows": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of rows to generate"
            },
            "shuffle": {
                "type": "boolean",
                "default": True,
                "description": "Whether to shuffle the generated data"
            },
            "configs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["names", "strategy"],
                    "properties": {
                        "names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Column names this strategy applies to"
                        },
                        "strategy": {
                            "type": "object",
                            "required": ["name", "params"],
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Strategy implementation name"
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Strategy-specific parameters"
                                }
                            }
                        }
                    }
                }
            },
            "file_writer": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["type", "params"],
                    "properties": {
                        "type": {"type": "string"},
                        "params": {"type": "object"}
                    }
                },
                "description": "Output file writer configurations"
            }
        }
    }
    
    return {
        "schema": schema,
        "description": "GenXData configuration schema"
    }

