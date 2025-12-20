import sys
import json
import logging
import inspect
import traceback
import subprocess
import os

# Add SUMO_HOME/tools to path
# if 'SUMO_HOME' in os.environ:
#     tools_path = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     if tools_path not in sys.path:
#         sys.path.append(tools_path)

from mcp_tools.simulation import run_simple_simulation
from mcp_tools.network import netconvert, netgenerate
from mcp_tools.route import random_trips, duarouter
from mcp_tools.signal import tls_cycle_adaptation
from mcp_tools.analysis import analyze_fcd
from workflows.sim_gen import sim_gen_workflow

# Configure logging to stderr to not interfere with stdout JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.tools = {}

    def tool(self, name=None, description=None):
        def decorator(func):
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or ""
            # Inspect parameters
            sig = inspect.signature(func)
            params = {
                "type": "object",
                "properties": {},
                "required": []
            }
            for param_name, param in sig.parameters.items():
                param_type = "string" # simplified type mapping
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                
                params["properties"][param_name] = {
                    "type": param_type,
                    "description": "" # Could parse from docstring
                }
                if param.default == inspect.Parameter.empty:
                    params["required"].append(param_name)
            
            self.tools[tool_name] = {
                "func": func,
                "schema": {
                    "name": tool_name,
                    "description": tool_desc,
                    "inputSchema": params
                }
            }
            return func
        return decorator

    def run(self):
        logger.info(f"Starting {self.name} v{self.version}")
        # On Windows, using sys.stdin might be tricky with some buffering, but usually works
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                if not line.strip():
                    continue
                request = json.loads(line)
                self.handle_request(request)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON: {line}")
            except Exception as e:
                logger.error(f"Error processing line: {e}")
                traceback.print_exc(file=sys.stderr)

    def handle_request(self, request):
        msg_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if method == "initialize":
            self.send_response(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            })
        elif method == "notifications/initialized":
            # No response needed
            pass
        elif method == "tools/list":
            self.send_response(msg_id, {
                "tools": [t["schema"] for t in self.tools.values()]
            })
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name]["func"](**tool_args)
                    self.send_response(msg_id, {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    })
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    self.send_error(msg_id, -32603, str(e))
            else:
                self.send_error(msg_id, -32601, f"Tool {tool_name} not found")
        elif method == "ping":
             self.send_response(msg_id, {})
        else:
            # Ignore other methods or return error
            if msg_id is not None:
                self.send_error(msg_id, -32601, f"Method {method} not found")

    def send_response(self, msg_id, result):
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def send_error(self, msg_id, code, message):
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

# Initialize Server
server = MCPServer("SUMO-MCP-Server", "0.1.0")

@server.tool(name="get_sumo_info", description="Get the version and path of the installed SUMO.")
def get_sumo_info():
    try:
        # Check sumo version
        result = subprocess.run(["sumo", "--version"], capture_output=True, text=True, check=True)
        version_output = result.stdout.splitlines()[0]
        
        # Check SUMO_HOME
        sumo_home = os.environ.get("SUMO_HOME", "Not Set")
        
        return f"SUMO Version: {version_output}\nSUMO_HOME: {sumo_home}"
    except Exception as e:
        return f"Error checking SUMO: {str(e)}"

@server.tool(name="run_simple_simulation", description="Run a SUMO simulation using a config file.")
def run_simple_simulation_tool(config_path: str, steps: int = 100):
    return run_simple_simulation(config_path, steps)

@server.tool(description="Convert OSM to SUMO network.")
def run_netconvert(osm_file: str, output_file: str, options: list = None):
    return netconvert(osm_file, output_file, options)

@server.tool(description="Generate abstract SUMO network (grid/spider).")
def run_netgenerate(output_file: str, grid: bool = True, grid_number: int = 3, options: list = None):
    return netgenerate(output_file, grid, grid_number, options)

@server.tool(description="Generate random trips for a network.")
def run_random_trips(net_file: str, output_file: str, end_time: int = 3600, period: float = 1.0, options: list = None):
    return random_trips(net_file, output_file, end_time, period, options)

@server.tool(description="Compute routes using duarouter.")
def run_duarouter(net_file: str, route_files: str, output_file: str, options: list = None):
    return duarouter(net_file, route_files, output_file, options)

@server.tool(description="Adapt TLS cycles.")
def run_tls_cycle_adaptation(net_file: str, route_files: str, output_file: str):
    return tls_cycle_adaptation(net_file, route_files, output_file)

@server.tool(description="Analyze FCD output.")
def run_analysis(fcd_file: str):
    return analyze_fcd(fcd_file)

@server.tool(description="Run Sim Gen & Eval Workflow.")
def run_sim_gen_workflow(output_dir: str, grid_number: int = 3, steps: int = 100):
    return sim_gen_workflow(output_dir, grid_number, steps)

if __name__ == "__main__":
    server.run()
