import logging
import os

logger = logging.getLogger("data_generator.writers.html")

def htmlWriter(df, params):
    """
    Write DataFrame to an HTML file.
    
    Args:
        df (pandas.DataFrame): DataFrame to write
        params (dict): Parameters including:
            - path_or_buf (str): Path to output HTML file
            - title (str, optional): Title for the HTML page
            - index (bool, optional): Whether to include index in output
            - classes (str, optional): CSS classes for the table
            - render_links (bool, optional): Convert URLs to HTML links
    
    Returns:
        None
    """
    try:
        # Support multiple path parameter names for flexibility
        path = params.get('output_path') or params.get('path_or_buf')
        if not path:
            raise ValueError("Missing path parameter (use 'output_path' or 'path_or_buf') for HTML writer")
            
        # Ensure the file has .html extension
        if not path.endswith(('.html', '.htm')):
            path = os.path.splitext(path)[0] + '.html'
            
        # Set default title if not provided
        if 'title' not in params:
            params['title'] = "Data Generator Output"
            
        # Set default table classes if not provided
        if 'classes' not in params:
            params['classes'] = 'table table-striped table-hover'
            
        # Add responsive Bootstrap styling
        bootstrap_css = """
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body { padding: 20px; }
            .container { max-width: 100%; }
            .table-responsive { margin-top: 20px; }
            tr { text-align: center; }
        </style>
        """
        
        # Extract custom options that aren't pandas to_html parameters
        include_bootstrap = params.pop('include_bootstrap', True)
        title = params.pop('title', 'Data Generator Output')
        classes = params.pop('classes', 'table table-striped')
        render_links = params.pop('render_links', True)
        
        # Export options for the HTML file (only pandas-compatible parameters)
        html_options = {
            'border': params.pop('border', 0),
            'index': params.pop('index', False),
            'escape': params.pop('escape', True),
            'na_rep': params.pop('na_rep', 'N/A'),
            'classes': classes
        }
        
        logger.info(f"Writing DataFrame with {len(df)} rows to HTML file: {path}")
        
        # Generate HTML content
        html_content = df.to_html(**html_options)
        
        # Add title and Bootstrap if requested
        if include_bootstrap:
            final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {bootstrap_css}
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="table-responsive">
            {html_content}
        </div>
    </div>
</body>
</html>"""
        else:
            final_html = html_content
            
        # Write the HTML content to the file
        with open(path, 'w') as f:
            f.write(final_html)
            
        logger.info(f"Successfully wrote HTML file: {path}")
        
    except Exception as e:
        logger.error(f"Error writing HTML file: {str(e)}")
        raise 