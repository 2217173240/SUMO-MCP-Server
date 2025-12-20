import subprocess
import sumolib
import os

def netconvert(osm_file: str, output_file: str, options: list = None) -> str:
    """
    Wrapper for SUMO netconvert. Converts OSM files to SUMO network files.
    """
    try:
        binary = sumolib.checkBinary('netconvert')
    except Exception as e:
        return f"Error finding netconvert: {e}"

    cmd = [binary, "--osm-files", osm_file, "-o", output_file]
    if options:
        # options should be a list of strings, e.g. ["--geometry.remove", "--ramps.guess"]
        cmd.extend(options)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Netconvert successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Netconvert failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Netconvert execution error: {str(e)}"

def netgenerate(output_file: str, grid: bool = True, grid_number: int = 3, options: list = None) -> str:
    """
    Wrapper for SUMO netgenerate. Generates abstract networks.
    """
    try:
        binary = sumolib.checkBinary('netgenerate')
    except Exception as e:
        return f"Error finding netgenerate: {e}"

    cmd = [binary, "-o", output_file]
    if grid:
        cmd.extend(["--grid", "--grid.number", str(grid_number)])
    
    if options:
        cmd.extend(options)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Netgenerate successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Netgenerate failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Netgenerate execution error: {str(e)}"
