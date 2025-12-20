import os
import sys
import traci
import sumolib

def run_simple_simulation(config_path: str, steps: int = 100) -> str:
    """
    Run a SUMO simulation using the given configuration file.
    
    Args:
        config_path: Path to the .sumocfg file.
        steps: Number of simulation steps to run.
        
    Returns:
        A summary string of the simulation execution.
    """
    if not os.path.exists(config_path):
        return f"Error: Config file not found at {config_path}"
    
    # Ensure SUMO_HOME is set
    if 'SUMO_HOME' not in os.environ:
         return "Error: SUMO_HOME environment variable is not set."

    try:
        sumo_binary = sumolib.checkBinary('sumo')
    except Exception as e:
        return f"Error finding sumo binary: {e}"
    
    # Start simulation
    # We use a random label to allow parallel runs if needed (though traci global lock is an issue)
    # Ideally use libsumo if available for speed, but traci is safer for now.
    cmd = [sumo_binary, "-c", config_path, "--no-step-log", "true", "--random"]
    
    try:
        traci.start(cmd)
        
        vehicle_counts = []
        for step in range(steps):
            traci.simulationStep()
            vehicle_counts.append(traci.vehicle.getIDCount())
        
        traci.close()
        
        avg_vehicles = sum(vehicle_counts) / len(vehicle_counts) if vehicle_counts else 0
        max_vehicles = max(vehicle_counts) if vehicle_counts else 0
        
        return (f"Simulation finished successfully.\n"
                f"Steps run: {steps}\n"
                f"Average vehicles: {avg_vehicles:.2f}\n"
                f"Max vehicles: {max_vehicles}")
                
    except Exception as e:
        try:
            traci.close()
        except:
            pass
        return f"Simulation error: {str(e)}"
