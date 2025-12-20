import subprocess
import os
import sys

def tls_cycle_adaptation(net_file: str, route_files: str, output_file: str) -> str:
    """
    Wrapper for tlsCycleAdaptation.py. Adapts traffic light cycles based on traffic demand.
    """
    if 'SUMO_HOME' not in os.environ:
        return "Error: SUMO_HOME not set"
    
    script = os.path.join(os.environ['SUMO_HOME'], 'tools', 'tlsCycleAdaptation.py')
    if not os.path.exists(script):
        return f"Error: script not found at {script}"
        
    cmd = [sys.executable, script, "-n", net_file, "-r", route_files, "-o", output_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"tlsCycleAdaptation successful.\nStdout: {result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"tlsCycleAdaptation failed.\nStderr: {e.stderr}\nStdout: {e.stdout}"
    except Exception as e:
        return f"Error: {str(e)}"
