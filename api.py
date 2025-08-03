import os
import tempfile
import zipfile
from io import BytesIO
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from core.orchestrator import DataOrchestrator
from core.strategy_mapping import get_all_strategy_names, get_all_strategy_schemas
from exceptions.param_exceptions import InvalidConfigParamException
from utils.generator_utils import validate_generator_config
from utils.logging import Logger

# Initialize API logger
logger = Logger.get_logger("api")

app = FastAPI(
    title="GenXData API",
    description="Synthetic data generation API with 13+ strategies and 175+ generators",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
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
    "*",  # Allow all origins for demo
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


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================


@app.get("/ping")
async def ping():
    """Simple health check endpoint."""
    return {"message": "pong", "status": "healthy"}


@app.get("/api/health")
async def health_check():
    """Comprehensive health check endpoint."""
    return {
        "status": "healthy",
        "service": "GenXData API",
        "version": "1.0.0",
        "timestamp": pd.Timestamp.now().isoformat(),
        "features": {
            "strategies": len(get_all_strategy_names()),
            "streaming": True,
            "batch_processing": True,
            "file_formats": [
                "CSV",
                "Excel",
                "JSON",
                "Parquet",
                "Feather",
                "HTML",
                "SQLite",
            ],
        },
    }


@app.get("/api/version")
async def get_version():
    """Get API version information."""
    return {
        "version": "1.0.0",
        "name": "GenXData API",
        "description": "Synthetic data generation API",
        "features": [
            "13+ data generation strategies",
            "175+ pre-built generators",
            "Multiple output formats",
            "Streaming and batch processing",
            "Real-time data generation",
        ],
    }


@app.get("/api/schemas/config")
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
                    "version": {"type": "string"},
                },
            },
            "column_name": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of column names",
            },
            "num_of_rows": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of rows to generate",
            },
            "shuffle": {
                "type": "boolean",
                "default": True,
                "description": "Whether to shuffle the generated data",
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
                            "description": "Column names this strategy applies to",
                        },
                        "strategy": {
                            "type": "object",
                            "required": ["name", "params"],
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Strategy implementation name",
                                },
                                "params": {
                                    "type": "object",
                                    "description": "Strategy-specific parameters",
                                },
                            },
                        },
                    },
                },
            },
            "file_writer": {
                "type": "object",
                "required": ["type", "params"],
                "properties": {
                    "type": {"type": "string"},
                    "params": {"type": "object"},
                },
                "description": "Output file wri ter configurations",
            },
        },
    }

    return {"schema": schema, "description": "GenXData configuration schema"}


# ============================================================================
# FRONTEND SERVING
# ============================================================================

# ============================================================================
# STRATEGY ENDPOINTS
# ============================================================================


@app.get("/get_all_strategies")
async def get_all_strategies():
    """Get all available data generation strategies."""
    return {"strategies": get_all_strategy_names()}


@app.get("/get_strategy_schemas")
async def get_strategy_schemas():
    """Get detailed schemas for all strategies."""
    return {"strategies": get_all_strategy_schemas()}


# ============================================================================
# FRONTEND SERVING
# ============================================================================


@app.get("/")
async def serve_frontend():
    """Serve the React frontend"""
    static_path = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "GenXData API", "status": "Frontend not built"}


# ============================================================================
# STATIC FILE SERVING (must be last to avoid intercepting API routes)
# ============================================================================


@app.get("/{filename:path}")
async def serve_static_files(filename: str):
    """Serve static files like vite.svg, favicon.ico, etc. from root"""
    # Only serve specific file types to avoid conflicts with API routes
    allowed_extensions = {
        ".svg",
        ".ico",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".txt",
        ".xml",
    }

    # Check if the filename has an allowed extension
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=404, detail="Not found")

    static_path = os.path.join(os.path.dirname(__file__), "static")
    file_path = os.path.join(static_path, filename)

    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="File not found")


# ============================================================================
# DATA GENERATION ENDPOINTS
# ============================================================================


@app.post("/generate_data")
async def generate_data(config: dict[str, Any]):
    """
    Generate data using the new DataOrchestrator architecture.

    Args:
        config: Configuration dictionary containing data generation parameters

    Returns:
        dict: Generated data and processing results
    """
    try:
        # Validate the configuration
        validate_generator_config(config)

        # Create orchestrator with the config
        orchestrator = DataOrchestrator(
            config=config,
            perf_report=False,  # Disable performance reporting for API calls
            stream=None,  # No streaming config for basic API calls
            batch=None,  # No batch config for basic API calls
            log_level="INFO",
        )

        # Run the data generation
        result = orchestrator.run()

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Data generation failed - check logs for details",
            )

        return {"data": result}

    except Exception as e:
        logger.error(f"Error in generate_data endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_and_download")
async def generate_and_download(config: dict[str, Any]):
    """
    Generate data based on config and return as a zip file containing the
    generated files.
    """
    try:
        # Force write_output to True to generate files
        config["write_output"] = True

        # Get the configured output file path and format
        file_writer = config.get("file_writer", [{}])[0]
        writer_type = file_writer.get("type", "CSV_WRITER")
        output_path = file_writer.get("params", {}).get("output_path", "")

        # Ensure output directory exists
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Validate the configuration
        validate_generator_config(config)

        # Create orchestrator with the config
        orchestrator = DataOrchestrator(
            config=config,
            perf_report=False,  # Disable performance reporting for API calls
            stream=None,  # No streaming config for basic API calls
            batch=None,  # No batch config for basic API calls
            log_level="INFO",
        )

        # Generate the data (this will create the output file)
        result = orchestrator.run()

        # Create a zip file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add the generated file to the zip
            if output_path and os.path.exists(output_path):
                # Get the filename from the path
                filename = os.path.basename(output_path)
                zip_file.write(output_path, filename)

                # Clean up the temporary file
                os.remove(output_path)
            else:
                # Fallback: create file from the returned data
                df = pd.DataFrame(result.get("df", []))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                df.to_csv(temp_file.name, index=False)
                zip_file.write(temp_file.name, "generated_data.csv")
                os.unlink(temp_file.name)

        zip_buffer.seek(0)

        # Get project name for filename
        project_name = config.get("metadata", {}).get("name", "generated_data")
        filename = f"{project_name.replace(' ', '_')}_data.zip"

        # Return the zip file as a streaming response
        return StreamingResponse(
            BytesIO(zip_buffer.read()),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to generate data", "message": str(e)},
        )


@app.post("/api/streaming/generate")
async def generate_streaming_data(
    config: dict[str, Any], stream_config: dict[str, Any]
):
    """
    Generate data using streaming mode for real-time processing.

    Args:
        config: Main data generation configuration
        stream_config: Streaming configuration (AMQP, Kafka, etc.)

    Returns:
        dict: Streaming processing results
    """
    try:
        # Validate the configuration
        validate_generator_config(config)

        # Create orchestrator with streaming config
        orchestrator = DataOrchestrator(
            config=config,
            perf_report=False,
            stream=stream_config,  # Use streaming config
            batch=None,
            log_level="INFO",
        )

        # Run the streaming data generation
        result = orchestrator.run()

        if result is None:
            raise HTTPException(
                status_code=500, detail="Streaming data generation failed"
            )

        return {"data": result, "mode": "streaming"}

    except Exception as e:
        logger.error(f"Error in streaming generate endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/generate")
async def generate_batch_data(config: dict[str, Any], batch_config: dict[str, Any]):
    """
    Generate data using batch processing mode.

    Args:
        config: Main data generation configuration
        batch_config: Batch processing configuration

    Returns:
        dict: Batch processing results
    """
    try:
        # Validate the configuration
        validate_generator_config(config)

        # Create orchestrator with batch config
        orchestrator = DataOrchestrator(
            config=config,
            perf_report=False,
            stream=None,
            batch=batch_config,  # Use batch config
            log_level="INFO",
        )

        # Run the batch data generation
        result = orchestrator.run()

        if result is None:
            raise HTTPException(status_code=500, detail="Batch data generation failed")

        return {"data": result, "mode": "batch"}

    except Exception as e:
        logger.error(f"Error in batch generate endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# CONFIGURATION ENDPOINTS
# ============================================================================


@app.post("/api/config/validate")
async def validate_config_api(config: dict):
    """Validate a configuration."""
    try:
        # Validate configuration
        is_valid = validate_generator_config(config)

        return {"valid": is_valid, "message": "Configuration is valid"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(InvalidConfigParamException)
async def invalid_config_param_exception_handler(
    request: Request, exc: InvalidConfigParamException
):
    return JSONResponse(
        status_code=400,
        content={
            "error_name": exc.__class__.__name__,
            "message": f"Configuration error: {exc.message}",
        },
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(
        status_code=500,
        content={
            "error_name": exc.__class__.__name__,
            "message": "Something went wrong while generating data.",
        },
    )
