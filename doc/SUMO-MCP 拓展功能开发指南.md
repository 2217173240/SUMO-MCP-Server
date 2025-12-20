# **SUMO-MCP 全流程指南：基于模型上下文协议的自主交通仿真与智能优化体系研究报告**

在现代城市交通管理与智慧城市建设的宏大背景下，微观交通仿真技术已成为评估交通政策、优化信号控制以及开发自动驾驶算法的核心工具。然而，传统的微观仿真软件如 SUMO（Simulation of Urban Mobility）虽然具备极高的建模精度与功能完整性，其高昂的技术门槛——包括复杂的网络下载、需求生成、仿真配置及结果分析流程，极大地限制了非专家用户（如城市规划者和决策者）的参与深度 1。2024年底由 Anthropic 推出的模型上下文协议（Model Context Protocol, MCP）为打破这一僵局提供了关键的技术路径。通过构建 SUMO-MCP 平台，研究者不仅实现了 SUMO 核心工具集的“即插即用”式集成，更通过大语言模型（LLM）的智能体（Agent）化转型，将数小时的手动脚本编写简化为秒级的自然语言指令，从而开启了自主交通仿真与实时优化设计的新纪元 3。

## **第一章 模型上下文协议（MCP）在交通仿真中的理论基础与架构范式**

模型上下文协议的核心哲学在于通过标准化的接口，消除人工智能应用与外部工具、数据源之间的通信隔阂。在 SUMO-MCP 的语境下，MCP 被视为连接 LLM “大脑”与 SUMO “物理引擎”的“USB-C 端口”，提供了一种通用的、可扩展的通信协议 5。

### **1.1 MCP 的架构组件与通信机制**

SUMO-MCP 遵循严谨的客户端-服务器（Client-Server）架构，这一设计确保了仿真逻辑与交互逻辑的解耦。其系统层级主要由四个核心参与方组成：MCP 宿主、MCP 客户端、MCP 服务器以及底层的 SUMO 核心引擎 7。

| 组件名称 | 核心职责 | 技术实现细节 |
| :---- | :---- | :---- |
| MCP 宿主 (Host) | 负责协调整体系统，管理与用户的 LLM 交互流程。 | 如 Cursor IDE、Claude Desktop 等集成环境 5。 |
| MCP 客户端 (Client) | 建立与服务器的 1:1 状态连接，负责能力协商与消息路由。 | 嵌入在宿主应用中的协议适配器，支持 JSON-RPC 2.0 7。 |
| MCP 服务器 (Server) | 暴露 SUMO 工具、资源与提示词模板，执行具体计算任务。 | 基于 FastMCP Python SDK 构建，通过 stdio 或 SSE 传输消息 10。 |
| SUMO 核心 (Core) | 执行微观交通动力学计算、车辆移动仿真及物理校验。 | 基于 C++ 开发的二进制文件（如 netconvert, sumo-gui） 13。 |

这种架构允许 MCP 服务器在本地环境运行，通过标准输入输出（stdio）与宿主应用进行高性能的进程间通信（IPC），或者在远程服务器上通过服务器发送事件（SSE）提供分布式支持 12。

### **1.2 JSON-RPC 2.0 协议层析**

SUMO-MCP 的通信依赖于轻量级的 JSON-RPC 2.0 消息格式。当智能体决定执行特定的仿真任务时，它会构造一个结构化的 JSON 对象。例如，调用网络转换工具 netconvert 的请求包含方法名、参数（输入文件名、输出路径）以及唯一的请求 ID。服务器在验证输入模式后，在独立的子进程中执行 SUMO 实用程序，并将执行结果、日志输出或结构化错误信息返回给客户端 8。这种强类型的交互模式极大地降低了参数误匹配的概率，实验数据表明，相比于直接通过命令行执行脚本，基于 MCP 的方法在复杂多步仿真中的错误率显著降低 1。

## **第二章 SUMO-MCP 开发全流程指南：从初始化到生产部署**

开发一个稳健的 SUMO-MCP 平台需要对 Python 环境、MCP SDK 以及 SUMO 核心工具链进行深度整合。以下是基于最新工业标准的开发路线图。

### **2.1 开发环境的精准配置**

在现代 Python 开发体系中，推荐使用 uv 工具链进行包管理，其极速的依赖解析能力能够确保 MCP 环境的绝对隔离与可重复性 17。

1. **基础环境初始化**：开发者需确保安装 Python 3.10 或更高版本。通过 uv init 初始化项目，并添加 mcp\[cli\] 及其相关依赖（如 pandas 用于数据分析，httpx 用于网络获取） 20。  
2. **SUMO 引擎集成**：核心步骤是设置 SUMO\_HOME 环境变量。这是 SUMO 的 Python 实用程序定位底层二进制文件的唯一凭据。在 Linux 环境下，通常指向 /usr/share/sumo 22。  
3. **FastMCP 实例化**：在服务器入口文件中，通过 FastMCP("SUMO-MCP-Server") 创建实例。该实例将作为所有自定义仿真工具、数据资源和交互提示词的注册中心 23。

### **2.2 工具（Tools）的封装与注册机制**

SUMO 的强大功能分散在数十个独立的命令行实用程序中。SUMO-MCP 的核心价值在于利用 @mcp.tool() 装饰器，将这些零散的工具转化为智能体可理解的原子化能力 23。

#### **交通工具链的分类模块化设计**

为了避免“工具过载”现象，SUMO-MCP 采用了动态导入（Dynamic Import）机制。服务器启动时仅注册基础管理模块，当智能体识别到特定用户意图后，才会按需加载相应的子模块 1。

| 子模块分类 | 包含的核心工具 | 业务逻辑说明 |
| :---- | :---- | :---- |
| Network (网络) | netconvert, netgenerate, osmGet | 处理从 OSM 到 SUMO XML 格式的拓扑转换与几何优化 4。 |
| Route (路径) | randomTrips, od2trips, duaRouter | 根据 OD 矩阵或随机概率分布生成具有物理意义的车辆轨迹 26。 |
| Signal (信号) | tlsCycleAdaptation, tlsCoordinator | 计算周期长度、绿信比，实现干道绿波优化 4。 |
| Analysis (分析) | cal\_metrics, compare\_metrics, report\_gen | 对仿真轨迹文件（fcd-output）进行后处理，生成 KPI 报告 1。 |

### **2.3 资源（Resources）与提示词模板（Prompts）的深度应用**

除了执行动作的“工具”外，SUMO-MCP 还利用“资源”暴露只读数据，以及利用“提示词模板”引导 LLM 进行策略推理。

* **资源集成**：通过 @mcp.resource()，系统可以将当前的仿真配置文件（.sumocfg）、实时的路网拥堵热力图数据或历史流量趋势作为上下文直接提供给智能体。这使得智能体能够基于“所见即所得”的仿真状态进行后续决策 28。  
* **提示词模板设计**：开发者可以预置如 explore\_topic\_prompt 的模板，指导智能体：“首先下载路网，然后生成随机需求，接着对比 Actuated 与 Fixed 信号控制，最后给出性能差异的经济学解释”。这种预置逻辑将复杂的工程经验编码到了交互流程中 30。

## **第三章 核心仿真自动化流程：从自然语言到可执行场景**

SUMO-MCP 的最大亮点在于其提供的两套预定义工作流，通过智能体编排，将碎片化的仿真步骤转化为端到端的服务。

### **3.1 场景生成与评估工作流（Sim Gen & Eval）**

该流程解决了“如何快速搭建一个仿真的基准环境”的问题。用户只需输入类似“模拟北京朝阳区晚高峰交通并评估不同控制策略”的指令，智能体即刻启动自动化流程 1：

1. **地理数据采集**：调用 osm\_download 辅助程序，根据地名解析经纬度并从 OpenStreetMap 镜像仓库抓取路网 XML 数据 1。  
2. **路网结构精修**：执行 netconvert。SUMO-MCP 自动配置参数以移除孤立节点、合并短匝道并根据道路类别分配速度限制 14。  
3. **交通需求建模**：智能体推断仿真步长（通常为 3600 秒）与车辆强度（如 5000 辆/小时），运行 randomTrips 生成路由文件，并支持集成外部 OD 矩阵 CSV 26。  
4. **多策略并行仿真**：系统同时配置四种控制方案：固定配时（Fixed-Time）、感应控制（Actuated）、Webster 优化方案以及基于偏置优化的绿波方案 1。

### **3.2 信号控制优化工作流（Signal Opt）**

该流程展示了智能体作为“虚拟交通工程师”的能力。它不仅运行仿真，更通过闭环反馈优化物理参数 1。

* **拥堵识别逻辑**：通过分析仿真过程中每条车道的平均等待时间（Waiting Time）与最大排队长度（Queue Length），智能体能够自动定位网络的瓶颈交叉口 1。  
* **智能参数精炼**：针对拥堵节点，智能体通过计算 PCE（乘用车当量）并应用改进的 Webster 公式（考虑饱和头时等参数），重新分配绿灯时间 27。  
* **效益评估**：实验显示，在雄安新区 5x5 的路网测试中，智能体驱动的优化使得全网平均延迟降低了 6.86%，而在关键拥堵节点 C2，排队时间更是下降了 21.45% 1。

| 评估指标 | 优化前 (Baseline) | 优化后 (Optimized) | 改善幅度 (%) |
| :---- | :---- | :---- | :---- |
| 平均行程时间 (s/veh) | 845.34 | 825.89 | 2.30% |
| 平均排队长度 (m) | 137.77 | 127.34 | 7.59% |
| 平均网络延迟 (s/veh) | 370.36 | 344.95 | 6.86% |
| 拥堵点 C2 等待时间 (s) | 110.5 | 86.8 | 21.45% |

1

## **第四章 创新功能扩展一：多智能体协作（Multi-Agent Collaboration）**

随着交通场景复杂度的提升，单一 LLM 智能体往往难以兼顾全局规划与底层实现的精细度。2025年的研究趋势正从单一智能体转向具备角色专业化特征的多智能体系统（LLM-MAS） 33。

### **4.1 基于 AgentSUMO 的目标导向推理**

AgentSUMO 代表了 SUMO-MCP 的高级演化形态。它引入了“互动规划协议”（Interactive Planning Protocol），要求智能体在执行动作前进行“澄清-推理”对话 34。

* **意图拆解与角色分配**：面对“降低区域排放”的任务，系统会激活多个专业 Agent。一名 Agent 专门负责路网编辑（如增加公交专用道），另一名负责需求分析（增加电动汽车渗透率），第三名负责信号配时调整以减少二次启停 33。  
* **状态字典管理**：为了确保多智能体间的步调一致，AgentSUMO 维护一个“仿真状态字典”。该字典记录所有生成的工件（网络文件、路由配置），并在每个 Agent 的系统提示词中注入上下文，防止重复计算与逻辑冲突 34。

### **4.2 MAGRPO 算法与协作协同效应**

为了解决大规模智能体集群的动作冲突，研究者提出了多智能体组相对策略优化（Multi-Agent Group Relative Policy Optimization, MAGRPO）算法 36。

1. **联合奖励模型**：系统不再仅仅关注单一车辆或交叉口的性能，而是将全网的吞吐量、碳排放水平以及紧急车辆优先通过率作为联合奖励 $R\_G$ 36。  
2. **Dec-POMDP 模型应用**：将 LLM 协作建模为“分散式部分可观测马尔可夫决策过程”。每个 Agent 仅拥有路网的局部视图，通过 MCP 协议交换经过简化的语义信息（如“我即将调整东向西方向绿灯”），从而在不消耗海量 Token 的前提下实现全局协同 37。

## **第五章 创新功能扩展二：强化学习集成（Reinforcement Learning Integration）**

强化学习（RL）是解决高度动态、非线性交通信号控制问题的金标准。SUMO-MCP 通过集成 SUMO-RL 库，实现了 LLM 高层决策与 RL 底层执行的高效耦合 39。

### **5.1 信号控制的 RL 环境建模**

在 SUMO-MCP 的 RL 扩展模块中，每一个交通信号灯（TLS）都被定义为一个 RL 代理。该代理通过 TraCI 接口从仿真引擎获取状态观测值 $S$ 22：

* **状态空间 (State Space)**：包含每条进入车道的车辆密度（Density）、排队车辆数（Queue，速度低于 $0.1 m/s$ 的车辆比例）以及当前活跃的相位 ID（One-hot 编码） 22。  
* **动作空间 (Action Space)**：离散的相位切换指令。每隔 delta\_time 秒，代理决定是维持当前绿灯还是切换至下一相位（并在切换前自动插入黄灯过渡） 22。  
* **奖励函数 (Reward Function)**：通常定义为累计车辆延迟的变化量：$\\Delta Delay \= D\_{t-1} \- D\_t$。若延迟减少，则给予正向反馈 22。

### **5.2 LLM-RL 协同架构：从感知到优化**

SUMO-MCP 的 RL 集成采用了两层结构。底层 RL 代理通过数千次的迭代仿真学习稳健的控制律；而顶层的 LLM 智能体则充当“策略监管者”，根据实时外部信息微调 RL 的目标函数 39。

例如，在发生紧急交通事故导致单向车道封闭时，LLM 智能体可以通过 MCP 的资源接口获取事件描述，并动态修改底层 RL 代理的奖励权重，优先保障受事故影响最小的干道流量。研究表明，这种组合方法在复杂路网下的 queue 管理效率提升了 64.5% 42。

## **第六章 创新功能扩展三：数字孪生与 V2X 通信仿真**

2025年交通仿真的另一个重要维度是向数字孪生（Digital Twin）及车联网（V2X）的演进。这要求仿真环境具备实时数据注入能力与多层通信协议模拟能力 47。

### **6.1 V2X 通信链路的仿真建模**

通过将 SUMO 与通信模拟器（如 OMNeT++ 或 ns-3）耦合，SUMO-MCP 能够模拟高度真实的车联网场景 13。

| 链路类型 | 仿真物理层指标 | 交通优化目标 |
| :---- | :---- | :---- |
| 车对车 (V2V) | 信噪比 (SNR), 丢包率 (PDR) | 模拟多车编队（Platooning）与碰撞预警。 |
| 车对基础设施 (V2I) | 边缘节点时延 (Latency) | 实现红绿灯倒计时预测与车速引导。 |
| 车对弱势群体 (V2P) | 非视距 (NLOS) 条件下的识别率 | 保障十字路口行人的通行安全。 |
| 移动 RSU 中继 | 移动雾节点覆盖范围 | 在复杂城市峡谷中维持通信稳定性。 |

48

在 simV2X 框架下，SUMO-MCP 可以利用 FastAPI 建立 Web 服务，实时可视化车辆间的消息交换。智能体可以通过调用这些服务，评估不同的边缘计算部署方案（Fog Computing）对交通吞吐量的实际影响 48。

### **6.2 交互式场景编辑与地理信息集成**

集成 Mapbox 的 Web 界面允许用户以直观的方式定义干预措施 47。LLM 辅助的数字孪生系统支持以下创新功能：

1. **动态拓扑热修复**：用户在聊天框中说“关闭林荫大道上的两条车道以进行维护”，智能体自动计算几何偏移，生成 SUMO 补丁文件（XML Patch），并通过 TraCI 的 reload 功能在不停止仿真的情况下实时应用变更 47。  
2. **泊车动态模拟**：针对常被忽视的停车巡航问题，2025年扩展包引入了路侧及室内停车库供应模型，模拟车辆在寻找车位时的额外里程与拥堵效应，支持根据动态停车费定价评估路权优化效果 47。

## **第七章 性能优化与工程最佳实践：迈向高效率仿真**

在大规模路网中，SUMO-MCP 的性能表现直接决定了其在工业界的部署前景。针对 MCP 协议的固有瓶颈，本章总结了关键的优化策略。

### **7.1 上下文效率优化：程序化工具调用**

传统的 LLM 工具调用需要多次推理往返：LLM 调用 A \-\> 结果返回 LLM \-\> LLM 推理后调用 B。在 2025 年，SUMO-MCP 引入了“程序化工具调用”（Programmatic Tool Calling）模式 50。

* **代码生成与沙箱执行**：LLM 智能体不再逐个调用工具，而是编写一段 Python 编排逻辑（使用沙箱内的 SUMO Python API）。  
* **惊人的效率提升**：实验数据显示，这种模式实现了 **98.7% 的 Token 消耗削减**（从 15万 Token 降至 2000 Token），并将执行速度提高了 60%。这是因为海量的中间过程数据（如数千辆车的瞬时位置信息）停留在沙箱执行环境中，仅有最终的汇总统计报告返回给 LLM 上下文 50。

### **7.2 高级 MCP 服务器管理策略**

为了确保服务器的稳定性与响应速度，建议遵循以下工程原则 53：

1. **分层安全模型 (Defense in Depth)**：MCP 工具具备执行 shell 命令的能力。必须实施严格的输入清洗，特别是针对文件路径参数，防止命令注入风险。同时，关键仿真操作应设置“人工确认”环节（Human-in-the-loop） 16。  
2. **状态持久化与审计日志**：通过集成如 LogFire 或标准 Python 记录器，对所有 MCP 调用进行实时跟踪。在 stdio 传输模式下，严禁将日志直接打印到 stdout（以免破坏 JSON-RPC 消息流），而应定向到独立的日志文件或 stderr 54。  
3. **容器化部署**：将 SUMO 引擎与 MCP 服务器打包为 Docker 镜像，不仅解决了 SUMO\_HOME 和库依赖的跨平台配置难题，更实现了多个隔离仿真实例的并行运行 58。

## **第八章 未来展望：2025年及以后的微观交通智能化**

微观交通仿真正处于从“被动模拟”向“主动辅助决策”跨越的关键期。

### **8.1 视觉仿真与沉浸式协作**

随着 NVIDIA Omniverse 等平台的成熟，SUMO-MCP 的可视化前端正在向高清 3D 动画转型。通过将微观物理数据流推送到渲染引擎，工程师不仅可以查看统计图表，更可以虚拟视角观察复杂的交叉口冲突，甚至利用 VR 设备进行多人协同设计 61。

### **8.2 心理学与经济学驱动的行为建模**

未来的 SUMO-MCP 将不再仅仅模拟“理想化的刚性车辆”。结合 LLM 对人类行为的深度理解，仿真模型将能够模拟驾驶员的心理特征，如在面临动态收费时的“诱饵效应”（Decoy Effect）或不同收入阶层对时间价值的差异化感知。这种“以人为中心”的建模将极大地提升仿真在社会福利分析中的参考价值 32。

## **结论与行动建议**

SUMO-MCP 的开发与部署标志着交通仿真从“专家专供工具”向“大众化智能服务”的跨越。通过将复杂的 SUMO 实用程序链封装在标准化的 MCP 协议之下，我们不仅实现了流程的极简自动化，更通过与多智能体系统、强化学习和数字孪生的深度融合，构建了一个具备自我进化能力的智能交通实验室。

对于交通研究机构与智慧城市开发团队，本文建议：首选 FastMCP 框架快速建立本地原型，利用 uv 管理底层复杂的物理引擎依赖；在扩展功能上，优先投入资源建立“提示词引导的 RL 优化”流程，并利用代码执行（Code Execution）模式降低长周期仿真的 Token 开销。随着 6G 通信和分布式 AI 的到来，SUMO-MCP 这种具备高度互操作性的协议范式，必将成为未来智慧城市实时管控的中枢架构。 1

#### **引用的著作**

1. 2506.03548v1.pdf  
2. SUMO-MCP: Leveraging the Model Context Protocol for Autonomous Traffic Simulation and Optimization \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/pdf/2506.03548](https://arxiv.org/pdf/2506.03548)  
3. SUMO-MCP: Leveraging the Model Context Protocol for Autonomous Traffic Simulation and Optimization \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2506.03548v1](https://arxiv.org/html/2506.03548v1)  
4. \[論文評述\] SUMO-MCP: Leveraging the Model Context Protocol for Autonomous Traffic Simulation and Optimization \- Moonlight, 访问时间为 十二月 19, 2025， [https://www.themoonlight.io/tw/review/sumo-mcp-leveraging-the-model-context-protocol-for-autonomous-traffic-simulation-and-optimization](https://www.themoonlight.io/tw/review/sumo-mcp-leveraging-the-model-context-protocol-for-autonomous-traffic-simulation-and-optimization)  
5. Model Context Protocol (MCP): A comprehensive introduction for developers \- Stytch, 访问时间为 十二月 19, 2025， [https://stytch.com/blog/model-context-protocol-introduction/](https://stytch.com/blog/model-context-protocol-introduction/)  
6. Anthropic's Model Context Protocol (MCP): A Deep Dive for Developers \- Medium, 访问时间为 十二月 19, 2025， [https://medium.com/@amanatulla1606/anthropics-model-context-protocol-mcp-a-deep-dive-for-developers-1d3db39c9fdc](https://medium.com/@amanatulla1606/anthropics-model-context-protocol-mcp-a-deep-dive-for-developers-1d3db39c9fdc)  
7. What is Model Context Protocol (MCP): Explained \- Composio, 访问时间为 十二月 19, 2025， [https://composio.dev/blog/what-is-model-context-protocol-mcp-explained](https://composio.dev/blog/what-is-model-context-protocol-mcp-explained)  
8. Architecture overview \- Model Context Protocol, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.io/docs/learn/architecture](https://modelcontextprotocol.io/docs/learn/architecture)  
9. The Ultimate Guide to Cursor MCP Servers for AI Engineers, 访问时间为 十二月 19, 2025， [https://skywork.ai/skypage/en/The-Ultimate-Guide-to-Cursor-MCP-Servers-for-AI-Engineers/1971383920724340736](https://skywork.ai/skypage/en/The-Ultimate-Guide-to-Cursor-MCP-Servers-for-AI-Engineers/1971383920724340736)  
10. Welcome to FastMCP 2.0\! \- FastMCP, 访问时间为 十二月 19, 2025， [https://gofastmcp.com/getting-started/welcome](https://gofastmcp.com/getting-started/welcome)  
11. Welcome to FastMCP 2.0\! \- FastMCP, 访问时间为 十二月 19, 2025， [https://gofastmcp.com/](https://gofastmcp.com/)  
12. Model Context Protocol (MCP): STDIO vs. SSE | by Naman Tripathi \- Medium, 访问时间为 十二月 19, 2025， [https://naman1011.medium.com/model-context-protocol-mcp-stdio-vs-sse-a2ac0e34643c](https://naman1011.medium.com/model-context-protocol-mcp-stdio-vs-sse-a2ac0e34643c)  
13. Eclipse SUMO \- Simulation of Urban MObility, 访问时间为 十二月 19, 2025， [https://eclipse.dev/sumo/](https://eclipse.dev/sumo/)  
14. Popular Simulation Platforms For The Internet Of Vehicles \- Open Source For You, 访问时间为 十二月 19, 2025， [https://www.opensourceforu.com/2025/12/popular-simulation-platforms-for-the-internet-of-vehicles/](https://www.opensourceforu.com/2025/12/popular-simulation-platforms-for-the-internet-of-vehicles/)  
15. Exposed MCP Servers: New AI Vulnerabilities & What to Do \- BitSight Technologies, 访问时间为 十二月 19, 2025， [https://www.bitsight.com/blog/exposed-mcp-servers-reveal-new-ai-vulnerabilities](https://www.bitsight.com/blog/exposed-mcp-servers-reveal-new-ai-vulnerabilities)  
16. Tools \- Model Context Protocol, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.io/specification/2025-06-18/server/tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)  
17. A Beginner's Guide to Use FastMCP \- Apidog, 访问时间为 十二月 19, 2025， [https://apidog.com/blog/fastmcp/](https://apidog.com/blog/fastmcp/)  
18. jlowin/fastmcp: The fast, Pythonic way to build MCP servers and clients \- GitHub, 访问时间为 十二月 19, 2025， [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)  
19. The official Python SDK for Model Context Protocol servers and clients \- GitHub, 访问时间为 十二月 19, 2025， [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)  
20. Model Context Protocol (MCP): A Guide With Demo Project \- DataCamp, 访问时间为 十二月 19, 2025， [https://www.datacamp.com/tutorial/mcp-model-context-protocol](https://www.datacamp.com/tutorial/mcp-model-context-protocol)  
21. How to Build Your Own MCP Server with Python \- freeCodeCamp, 访问时间为 十二月 19, 2025， [https://www.freecodecamp.org/news/how-to-build-your-own-mcp-server-with-python/](https://www.freecodecamp.org/news/how-to-build-your-own-mcp-server-with-python/)  
22. LucasAlegre/sumo-rl: Reinforcement Learning environments for Traffic Signal Control with SUMO. Compatible with Gymnasium, PettingZoo, and popular RL libraries. \- GitHub, 访问时间为 十二月 19, 2025， [https://github.com/LucasAlegre/sumo-rl](https://github.com/LucasAlegre/sumo-rl)  
23. Tools \- FastMCP, 访问时间为 十二月 19, 2025， [https://gofastmcp.com/servers/tools](https://gofastmcp.com/servers/tools)  
24. How to Create an MCP Server in Python \- FastMCP, 访问时间为 十二月 19, 2025， [https://gofastmcp.com/tutorials/create-mcp-server](https://gofastmcp.com/tutorials/create-mcp-server)  
25. netconvert \- SUMO Documentation, 访问时间为 十二月 19, 2025， [https://sumo.dlr.de/docs/netconvert.html](https://sumo.dlr.de/docs/netconvert.html)  
26. sumo/docs/web/docs/Definition\_of\_Vehicles,\_Vehicle\_Types,\_and\_Routes.md at main, 访问时间为 十二月 19, 2025， [https://github.com/eclipse-sumo/sumo/blob/master/docs/web/docs/Definition\_of\_Vehicles,\_Vehicle\_Types,\_and\_Routes.md](https://github.com/eclipse-sumo/sumo/blob/master/docs/web/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.md)  
27. sumo/tools/tlsCycleAdaptation.py at main · eclipse-sumo/sumo \- GitHub, 访问时间为 十二月 19, 2025， [https://github.com/eclipse/sumo/blob/master/tools/tlsCycleAdaptation.py](https://github.com/eclipse/sumo/blob/master/tools/tlsCycleAdaptation.py)  
28. Resources & Templates \- FastMCP, 访问时间为 十二月 19, 2025， [https://gofastmcp.com/servers/resources](https://gofastmcp.com/servers/resources)  
29. Exploring MCP Primitives: Tools, Resources, and Prompts | CodeSignal Learn, 访问时间为 十二月 19, 2025， [https://codesignal.com/learn/courses/developing-and-integrating-a-mcp-server-in-python/lessons/exploring-and-exposing-mcp-server-capabilities-tools-resources-and-prompts](https://codesignal.com/learn/courses/developing-and-integrating-a-mcp-server-in-python/lessons/exploring-and-exposing-mcp-server-capabilities-tools-resources-and-prompts)  
30. Building an MCP Server and Client with FastMCP 2.0 \- DataCamp, 访问时间为 十二月 19, 2025， [https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp](https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp)  
31. Prompts \- Model Context Protocol, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.io/specification/2025-06-18/server/prompts](https://modelcontextprotocol.io/specification/2025-06-18/server/prompts)  
32. Speak to Simulate: An LLM-Guided Agentic Framework for Traffic Simulation in SUMO, 访问时间为 十二月 19, 2025， [https://www.researchgate.net/publication/397182078\_Speak\_to\_Simulate\_An\_LLM-Guided\_Agentic\_Framework\_for\_Traffic\_Simulation\_in\_SUMO](https://www.researchgate.net/publication/397182078_Speak_to_Simulate_An_LLM-Guided_Agentic_Framework_for_Traffic_Simulation_in_SUMO)  
33. LLMs and Multi-Agent Systems: The Future of AI in 2025 \- Classic Informatics, 访问时间为 十二月 19, 2025， [https://www.classicinformatics.com/blog/how-llms-and-multi-agent-systems-work-together-2025](https://www.classicinformatics.com/blog/how-llms-and-multi-agent-systems-work-together-2025)  
34. AgentSUMO: An Agentic Framework for Interactive Simulation Scenario Generation in SUMO via Large Language Models \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2511.06804v1](https://arxiv.org/html/2511.06804v1)  
35. AgentSUMO: An Agentic Framework for Interactive Simulation Scenario Generation in SUMO via Large Language Models \- ChatPaper, 访问时间为 十二月 19, 2025， [https://chatpaper.com/paper/207909](https://chatpaper.com/paper/207909)  
36. LLM Collaboration With Multi-Agent Reinforcement Learning \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/pdf/2508.04652](https://arxiv.org/pdf/2508.04652)  
37. LLM Collaboration with Multi-Agent Reinforcement Learning \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2508.04652v2](https://arxiv.org/html/2508.04652v2)  
38. LLMs for Multi-Agent Cooperation | Xueguang Lyu, 访问时间为 十二月 19, 2025， [https://xue-guang.com/post/llm-marl/](https://xue-guang.com/post/llm-marl/)  
39. Adaptive Traffic Management System Using Reinforcement Learning \- IJRASET, 访问时间为 十二月 19, 2025， [https://www.ijraset.com/best-journal/adaptive-traffic-management-system-using-reinforcement-learning](https://www.ijraset.com/best-journal/adaptive-traffic-management-system-using-reinforcement-learning)  
40. Advances in reinforcement learning for traffic signal control: a review of recent progress | Intelligent Transportation Infrastructure | Oxford Academic, 访问时间为 十二月 19, 2025， [https://academic.oup.com/iti/article/8125227](https://academic.oup.com/iti/article/8125227)  
41. Deep reinforcement learning for traffic light control optimization in multi-modal simulation of SUMO \- TU Delft Repositories, 访问时间为 十二月 19, 2025， [https://resolver.tudelft.nl/44154747-ccff-44c8-9983-e89f1364e1a9](https://resolver.tudelft.nl/44154747-ccff-44c8-9983-e89f1364e1a9)  
42. Multi-agent reinforcement learning framework for autonomous traffic signal control in smart cities \- Frontiers, 访问时间为 十二月 19, 2025， [https://www.frontiersin.org/journals/mechanical-engineering/articles/10.3389/fmech.2025.1650918/full](https://www.frontiersin.org/journals/mechanical-engineering/articles/10.3389/fmech.2025.1650918/full)  
43. Optimizing Traffic Flow Using sumo-RL: An Integration of SUMO and Reinforcement Learning | by Shazia Parween | Medium, 访问时间为 十二月 19, 2025， [https://medium.com/@shaziaparween333/optimizing-traffic-flow-using-sumo-rl-an-integration-of-sumo-and-reinforcement-learning-455514d2eec9](https://medium.com/@shaziaparween333/optimizing-traffic-flow-using-sumo-rl-an-integration-of-sumo-and-reinforcement-learning-455514d2eec9)  
44. OUT OF THE PAST: AN AI-ENABLED PIPELINE FOR TRAFFIC SIMULATION FROM NOISY, MULTIMODAL DETECTOR DATA AND STAKEHOLDER FEEDBACK \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2505.21349v2](https://arxiv.org/html/2505.21349v2)  
45. Exploring Traffic Simulation and Cybersecurity Strategies Using Large Language Models, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2506.16699v1](https://arxiv.org/html/2506.16699v1)  
46. Advances in reinforcement learning for traffic signal control: a review of recent progress, 访问时间为 十二月 19, 2025， [https://www.researchgate.net/publication/391481605\_Advances\_in\_reinforcement\_learning\_for\_traffic\_signal\_control\_a\_review\_of\_recent\_progress](https://www.researchgate.net/publication/391481605_Advances_in_reinforcement_learning_for_traffic_signal_control_a_review_of_recent_progress)  
47. LLM-Powered Digital Twins for Interactive Urban Mobility Simulation: Integrating SUMO with AI Agents \- OpenReview, 访问时间为 十二月 19, 2025， [https://openreview.net/pdf?id=vEZtmnqmtO](https://openreview.net/pdf?id=vEZtmnqmtO)  
48. V2X Simulation Framework for Intelligent Transportation Systems\[v1\] | Preprints.org, 访问时间为 十二月 19, 2025， [https://www.preprints.org/manuscript/202511.0575/v1](https://www.preprints.org/manuscript/202511.0575/v1)  
49. Survey of LLMs and AI Agents in V2X: Simulation, Analysis & Architectures \- ResearchGate, 访问时间为 十二月 19, 2025， [https://www.researchgate.net/publication/390611486\_Survey\_of\_LLMs\_and\_AI\_Agents\_in\_V2X\_Simulation\_Analysis\_Architectures](https://www.researchgate.net/publication/390611486_Survey_of_LLMs_and_AI_Agents_in_V2X_Simulation_Analysis_Architectures)  
50. Code execution with MCP: Building more efficient agents \- Anthropic, 访问时间为 十二月 19, 2025， [https://www.anthropic.com/engineering/code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp)  
51. Introducing advanced tool use on the Claude Developer Platform \- Anthropic, 访问时间为 十二月 19, 2025， [https://www.anthropic.com/engineering/advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use)  
52. Anthropic's Code Execution with MCP: A Paradigm Shift in AI Tool Integration \- EffiFlow, 访问时间为 十二月 19, 2025， [https://jangwook.net/en/blog/en/anthropic-code-execution-mcp/](https://jangwook.net/en/blog/en/anthropic-code-execution-mcp/)  
53. MCP Best Practices: Architecture & Implementation Guide, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.info/docs/best-practices/](https://modelcontextprotocol.info/docs/best-practices/)  
54. Standardizing AI Agent Integration: How to Build Scalable, Secure, and Maintainable Multi-Agent Systems with Anthropic's MCP \- deepsense.ai, 访问时间为 十二月 19, 2025， [https://deepsense.ai/blog/standardizing-ai-agent-integration-how-to-build-scalable-secure-and-maintainable-multi-agent-systems-with-anthropics-mcp/](https://deepsense.ai/blog/standardizing-ai-agent-integration-how-to-build-scalable-secure-and-maintainable-multi-agent-systems-with-anthropics-mcp/)  
55. Tools \- Model Context Protocol （MCP）, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.info/docs/concepts/tools/](https://modelcontextprotocol.info/docs/concepts/tools/)  
56. Specification \- Model Context Protocol, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.io/specification/2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)  
57. Model Context Protocol, 访问时间为 十二月 19, 2025， [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)  
58. 5 Best Practices for Building MCP Servers \- Snyk, 访问时间为 十二月 19, 2025， [https://snyk.io/articles/5-best-practices-for-building-mcp-servers/](https://snyk.io/articles/5-best-practices-for-building-mcp-servers/)  
59. MCP server for Sumologic \- GitHub, 访问时间为 十二月 19, 2025， [https://github.com/samwang0723/mcp-sumologic](https://github.com/samwang0723/mcp-sumologic)  
60. Traffic control RL environment with OpenEnv and SUMO \- Lightning AI, 访问时间为 十二月 19, 2025， [https://lightning.ai/lightning-ai/environments/traffic-control-rl-environment](https://lightning.ai/lightning-ai/environments/traffic-control-rl-environment)  
61. Simulation modeling trends to follow in 2025 \- AnyLogic, 访问时间为 十二月 19, 2025， [https://www.anylogic.com/blog/simulation-modeling-trends-to-follow-in-2025/](https://www.anylogic.com/blog/simulation-modeling-trends-to-follow-in-2025/)  
62. LLM-Guided Reinforcement Learning with Representative Agents for Traffic Modeling \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/abs/2511.06260](https://arxiv.org/abs/2511.06260)  
63. LLM-Guided Reinforcement Learning with Representative Agents for Traffic Modeling \- arXiv, 访问时间为 十二月 19, 2025， [https://arxiv.org/html/2511.06260](https://arxiv.org/html/2511.06260)