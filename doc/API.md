# SUMO-MCP API 参考

## 核心工具 (Tools)

### Network
*   **run_netconvert**
    *   `osm_file` (string): OSM 输入文件路径。
    *   `output_file` (string): SUMO 网络文件输出路径 (.net.xml)。
    *   `options` (list, optional): 额外参数列表。
*   **run_netgenerate**
    *   `output_file` (string): 输出路径。
    *   `grid` (boolean): 是否生成网格 (True/False)。
    *   `grid_number` (integer): 网格维度 (如 3 表示 3x3)。
    *   `options` (list, optional): 额外参数。

### Route
*   **run_random_trips**
    *   `net_file` (string): 网络文件路径。
    *   `output_file` (string): 行程文件输出路径 (.trips.xml)。
    *   `end_time` (integer): 模拟生成截止时间 (秒)。
    *   `period` (float): 车辆生成平均间隔 (秒)。
*   **run_duarouter**
    *   `net_file` (string): 网络文件。
    *   `route_files` (string): 行程文件输入。
    *   `output_file` (string): 路由文件输出 (.rou.xml)。

### Simulation & Analysis
*   **run_simple_simulation**
    *   `config_path` (string): .sumocfg 配置文件路径。
    *   `steps` (integer): 模拟步数。
*   **run_analysis**
    *   `fcd_file` (string): FCD 输出文件路径 (XML格式)。

### Signal Control
*   **run_tls_cycle_adaptation**
    *   `net_file` (string): 网络文件。
    *   `route_files` (string): 路由文件。
    *   `output_file` (string): 输出的新网络文件或TLS程序。

### Workflows
*   **run_sim_gen_workflow**
    *   `output_dir` (string): 工作流输出目录。
    *   `grid_number` (integer): 网格大小。
    *   `steps` (integer): 模拟步数。
    *   **描述**: 自动化执行 Netgenerate -> RandomTrips -> Duarouter -> Config Creation -> Simulation -> Analysis 流程。
