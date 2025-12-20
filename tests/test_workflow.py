import subprocess
import json
import os
import shutil

def test_workflow():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "output_workflow"))
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    server_path = os.path.join(os.path.dirname(__file__), "..", "src", "server.py")
    
    # We must use the conda python
    python_exe = r"D:\anaconda\envs\sumo-rl\python.exe"
    
    process = subprocess.Popen(
        [python_exe, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    # Initialize
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}) + "\n")
    process.stdin.flush()
    process.stdout.readline()
    
    process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    process.stdin.flush()
    
    # Call Workflow
    print("Calling run_sim_gen_workflow...")
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "run_sim_gen_workflow",
            "arguments": {
                "output_dir": output_dir,
                "grid_number": 3,
                "steps": 50
            }
        }
    }
    process.stdin.write(json.dumps(req) + "\n")
    process.stdin.flush()
    
    line = process.stdout.readline()
    if not line:
        print("No output. Stderr:")
        print(process.stderr.read())
        return

    response = json.loads(line)
    if "error" in response:
        print("Error:", response["error"])
        assert False
        
    content = response["result"]["content"][0]["text"]
    print("Workflow Output:\n", content)
    
    assert "Workflow Completed Successfully" in content
    assert "Average Speed" in content
    
    process.terminate()

if __name__ == "__main__":
    test_workflow()
