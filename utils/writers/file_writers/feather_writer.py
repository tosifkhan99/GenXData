import os


def featherWriter(df, params):
    """
    Write DataFrame to a Feather file.

    Feather is a fast, lightweight binary columnar format that is designed for high-performance
    data interoperability between multiple languages and environments.

    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters including:
            - path (str): Path to output Feather file
            - compression (str, optional): Compression algorithm ('zstd', 'lz4', 'uncompressed')
            - chunksize (int, optional): Number of rows per chunk for writing large files

    Returns:
        None
    """
    try:
        # Support multiple path parameter names for flexibility
        path = params.get("output_path") or params.get("path")
        if not path:
            raise ValueError(
                "Missing path parameter (use 'output_path' or 'path') for Feather writer"
            )

        # Ensure the file has .feather extension
        if not path.endswith(".feather"):
            path = os.path.splitext(path)[0] + ".feather"

        # Create a copy of params without path-related keys and any None values
        writer_params = {
            k: v
            for k, v in params.items()
            if k not in ["output_path", "path"] and v is not None
        }

        # Set defaults for common parameters
        if "compression" not in writer_params:
            writer_params["compression"] = "zstd"

        # Write the dataframe to a Feather file
        df.to_feather(path, **writer_params)

    except ImportError:
        raise
    except Exception:
        raise
