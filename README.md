# SUMO-MCP: 基于模型上下文协议的自主交通仿真平台

SUMO-MCP 是一个连接大语言模型 (LLM) 与 Eclipse SUMO 交通仿真引擎的中间件。通过 Model Context Protocol (MCP)，它允许 AI 智能体直接调用 SUMO 的核心功能，实现从路网生成、需求建模到仿真运行与结果分析的全流程自动化。

## 功能特性

*   **MCP 兼容**: 提供标准的 JSON-RPC 2.0 接口，可集成到 Claude Desktop、Cursor 或其他 MCP 宿主中。
*   **工具链集成**:
    *   `run_netconvert`: 调用 `netconvert` 进行路网转换。
    *   `run_netgenerate`: 快速生成网格或蜘蛛网路网。
    *   `run_random_trips`: 生成随机交通需求。
    *   `run_duarouter`: 路由计算。
    *   `run_tls_cycle_adaptation`: 信号配时优化。
*   **自动化工作流**:
    *   `run_sim_gen_workflow`: 一键执行 "生成路网 -> 生成需求 -> 仿真 -> 分析" 的完整闭环。
*   **实时分析**: 解析 FCD (Floating Car Data) 输出，提供速度、流量等统计指标。

## 环境要求

*   **操作系统**: Windows / Linux / macOS
*   **Python**: 3.8+ (推荐使用 Conda 环境)
*   **SUMO**: Eclipse SUMO 1.23+ (需配置 `SUMO_HOME` 环境变量)

## 安装指南

1.  **克隆仓库**:
    ```bash
    git clone <repository_url>
    cd sumo-mcp
    ```

2.  **安装依赖**:
    如果你使用 Conda (推荐 `sumo-rl` 环境):
    ```bash
    conda activate sumo-rl
    pip install pandas
    ```
    或者使用 pip:
    ```bash
    pip install sumolib traci pandas
    ```

3.  **配置 SUMO**:
    确保 `SUMO_HOME` 环境变量指向 SUMO 安装目录 (例如 `F:\sumo`).

## 启动服务

使用 Python 启动 MCP 服务器：

```bash
# Windows (使用完整路径或激活环境后)
python src/server.py
```

服务器启动后将监听标准输入 (stdin) 的 JSON-RPC 消息。

## 快速开始 (LLM 提示词示例)

在配置了 MCP 的 AI 助手中，你可以尝试以下指令：

> "请帮我生成一个 3x3 的网格路网，模拟 1000 步的交通流，并告诉我平均车速是多少。"

系统将自动调用 `run_sim_gen_workflow` 工具完成任务。

## 项目结构

```
sumo-mcp/
├── src/
│   ├── server.py           # MCP 服务器入口
│   ├── mcp_tools/          # 核心工具模块
│   │   ├── network.py      # 路网工具
│   │   ├── route.py        # 路径工具
│   │   ├── signal.py       # 信号工具
│   │   └── analysis.py     # 分析工具
│   └── workflows/          # 自动化工作流
│       └── sim_gen.py
├── tests/                  # 测试用例
└── requirements.txt        # 依赖列表
```

## 许可证

MIT License
