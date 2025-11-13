# HA IP Monitor - 项目需求文档

## 🚀 项目概述

**项目名称**: `HA_IP_Monitor`  
**项目类型**: Home Assistant HACS自定义集成  
**目标**: 为家庭服务器提供企业级安全监控和IP威胁管理  
**开发时间**: 2025年11月12日开始  

---

## 📋 项目背景

### 🏗️ 当前基础架构
```
iPhone → OpenVPN(VPS) → WireGuard隧道 → Home Server(HA) → 家庭网络
                ↓                           ↓
           167.179.78.163              192.168.0.190
```

### 🛡️ 现有安全配置
- **VPS**: Vultr日本节点，Ubuntu 24.04，已禁用root SSH
- **防火墙**: UFW已启用，22条安全规则
- **VPN服务**: OpenVPN服务器 + WireGuard隧道
- **Home Assistant**: Docker部署在家庭服务器

### ⚠️ 当前痛点
1. **手动监控**: 需要SSH到VPS逐个执行命令检查安全状态
2. **攻击不可视**: 无法直观看到攻击来源和频率
3. **响应滞后**: 发现威胁到处理有时间差
4. **操作繁琐**: 封锁IP需要手动执行UFW命令

---

## 🎯 产品愿景

### 💡 核心理念
**"让每个家庭服务器都拥有企业级安全监控"**

### 🔥 目标用户
- 家庭服务器运维者
- Home Assistant用户
- 网络安全关注者
- 技术爱好者

### 🏆 产品目标
- **一键安装**: HACS商店直接安装，无需复杂配置
- **可视化管理**: 在HA界面直观查看和管理安全威胁
- **自动化响应**: 检测到威胁自动封锁或告警
- **多平台支持**: 适配不同VPS和网络环境

---

## 📊 功能需求

### 🔥 核心功能（MVP版本）

#### 1. **威胁监控仪表盘**
```yaml
显示内容:
  - 今日被阻止IP数量
  - SSH攻击尝试次数  
  - VPN攻击尝试次数
  - 系统安全状态指示
  
可视化:
  - 24小时攻击趋势图
  - 攻击来源地理分布
  - 威胁等级饼状图
```

#### 2. **实时威胁列表**
```yaml
威胁IP列表:
  - IP地址
  - 攻击次数
  - 来源国家/地区
  - 最后攻击时间
  - 威胁等级评分
  
操作功能:
  - 单击查看详情
  - 长按立即封锁
  - 批量选择操作
```

#### 3. **一键IP管理**
```yaml
单IP操作:
  - 立即封锁IP
  - 解除封锁IP
  - 添加到白名单
  - 深度威胁分析
  
批量操作:
  - 选择多个IP批量封锁
  - 清理历史封锁记录
  - 导出威胁IP列表
  - 批量白名单管理
```

#### 4. **紧急安全响应**
```yaml
紧急锁定:
  - 一键限制SSH访问
  - 暂停新VPN连接
  - 启动安全模式
  - 发送紧急通知
  
自动响应:
  - 攻击次数达阈值自动封锁
  - 异常流量自动告警
  - 可疑行为模式检测
```

### ⚡ 增强功能（V2.0版本）

#### 5. **威胁情报分析**
```yaml
IP情报:
  - 地理位置定位
  - ISP信息查询
  - 威胁数据库比对
  - 历史攻击记录
  
分析功能:
  - 攻击模式识别
  - 威胁等级评估
  - 关联攻击检测
  - 预测性分析
```

#### 6. **多渠道通知系统**
```yaml
通知方式:
  - HA推送通知
  - 移动端App通知
  - 邮件告警
  - 微信/企业微信推送
  
告警级别:
  - 信息级: 日常攻击统计
  - 警告级: 攻击频率异常
  - 严重级: 疑似突破尝试
  - 紧急级: 系统安全威胁
```

#### 7. **高级自动化**
```yaml
智能响应:
  - 基于AI的威胁识别
  - 动态阈值调整
  - 自适应防护策略
  - 学习用户行为模式
  
集成功能:
  - 与其他安全工具联动
  - 支持自定义脚本
  - API开放接口
  - 第三方服务集成
```

---

## 🛠️ 技术规格

### 📦 插件架构

```
HA_IP_Monitor/
├── __init__.py                 # 插件初始化
├── manifest.json              # HACS元数据
├── config_flow.py             # 配置向导
├── const.py                   # 常量定义
├── coordinator.py             # 数据协调器
├── sensor.py                  # 传感器实体
├── services.yaml             # 服务定义
├── translations/             # 多语言支持
│   ├── en.json
│   └── zh.json
├── frontend/                 # 前端界面
│   ├── ip-monitor-card.js    # 自定义卡片
│   └── styles.css
└── remote_scripts/          # 远程部署脚本
    ├── vps_monitor.py       # VPS监控脚本
    ├── installer.sh         # 自动安装脚本
    └── config_template.yaml # 配置模板
```

### 🌐 系统架构

```
Home Assistant (192.168.0.190)
├── HA_IP_Monitor集成
├── 自定义仪表盘卡片
├── 自动化规则
└── 通知服务
    ↓ WireGuard隧道
VPS (167.179.78.163)
├── IP监控API (Python Flask)
├── UFW防火墙管理
├── 日志分析脚本
└── 威胁检测引擎
```

### 📡 通信协议

```yaml
HA → VPS 通信:
  协议: HTTP/HTTPS over WireGuard
  端口: 5001 (自定义API端口)
  认证: API Token + IP白名单
  数据格式: JSON
  
VPS → HA 数据推送:
  方式: RESTful API轮询
  频率: 每60秒更新一次
  异常时: 立即推送告警
```

---

## 🎨 用户界面设计

### 📱 主要界面布局

#### **安全概览页面**
```
┌─────────────────────────────────────────────────┐
│  🛡️ HA IP Monitor - 安全中心                    │
├─────────────────────────────────────────────────┤
│ 📊 今日威胁概览          │ 🌍 攻击来源分布         │
│ • 被阻止IP: 47个         │ [交互式世界地图]        │
│ • SSH攻击: 156次         │ • 🇨🇳 中国: 23次       │
│ • VPN攻击: 38次          │ • 🇺🇸 美国: 15次       │
│ • 状态: 🟢 安全          │ • 🇷🇺 俄罗斯: 9次      │
├─────────────────────────┼─────────────────────────┤
│ 🚨 实时威胁列表          │ ⚡ 快速操作面板         │
│ 185.200.116.43 [封锁]   │ [🚫 封锁选中IP]        │
│ 207.90.244.11  [分析]   │ [📋 批量管理]           │
│ 113.11.231.56  [监控]   │ [🚨 紧急锁定]          │
│ 2.57.121.112   [详情]   │ [📊 生成报告]          │
├─────────────────────────┼─────────────────────────┤
│ 📈 攻击趋势图            │ 🔧 系统状态             │
│ [24小时攻击趋势图表]     │ VPS: 🟢 CPU 15%        │
│                         │ SSH: 🟢 运行中          │
│                         │ VPN: 🟢 4个连接         │
└─────────────────────────┴─────────────────────────┘
```

#### **IP详情弹窗**
```
┌─────────────────────────────────────┐
│  🕵️ IP威胁分析: 185.200.116.43      │
├─────────────────────────────────────┤
│  📍 地理位置: 中国北京               │
│  🏢 ISP: 阿里云                     │
│  ⚠️  威胁等级: 高危 (8.5/10)        │
│  📊 攻击次数: 156次                 │
│  🕐 首次攻击: 2小时前               │
│  🎯 攻击类型: SSH暴力破解           │
├─────────────────────────────────────┤
│  📈 攻击时间线图表                   │
│  [显示24小时攻击频率图]              │
├─────────────────────────────────────┤
│  [🚫 立即封锁] [📋 加入监控] [❌ 关闭] │
└─────────────────────────────────────┘
```

---

## ⚙️ 配置规格

### 🔧 用户配置界面

#### **初始设置向导**
```yaml
步骤1 - VPS连接配置:
  VPS地址: [文本框] 167.179.78.163
  SSH端口: [数字框] 22 
  用户名: [文本框] cody
  认证方式: [选择] 密码 / SSH密钥
  测试连接: [按钮] 验证连接

步骤2 - 监控服务配置:
  监控范围: [多选框]
    - ☑ SSH登录监控
    - ☑ OpenVPN连接监控  
    - ☑ WireGuard隧道监控
    - ☐ 自定义端口监控
  
  告警阈值: [滑块]
    - SSH失败次数: 5次/5分钟
    - 攻击IP数量: 10个/小时
    - 异常流量: 100MB/分钟

步骤3 - 响应策略配置:
  自动封锁: [开关] 启用
  封锁时长: [选择] 24小时 / 永久 / 自定义
  白名单IP: [文本区域] 输入可信IP段
  通知方式: [多选] 移动推送 / 邮件 / 微信

步骤4 - 部署确认:
  [预览] 即将执行的操作
  [部署] 开始自动部署
  [测试] 连接和功能测试
```

### 📊 传感器配置

```yaml
# 自动生成的传感器列表
sensor:
  # 基础统计传感器
  - platform: ha_ip_monitor
    name: "今日被阻止IP数量"
    entity_id: sensor.blocked_ips_today
    
  - platform: ha_ip_monitor  
    name: "SSH攻击次数"
    entity_id: sensor.ssh_attacks_today
    
  - platform: ha_ip_monitor
    name: "VPN攻击次数"  
    entity_id: sensor.vpn_attacks_today
    
  # 系统状态传感器
  - platform: ha_ip_monitor
    name: "VPS系统状态"
    entity_id: sensor.vps_system_status
    
  - platform: ha_ip_monitor
    name: "防火墙规则数量"
    entity_id: sensor.firewall_rules_count
    
  # 威胁分析传感器
  - platform: ha_ip_monitor
    name: "当前威胁等级"
    entity_id: sensor.current_threat_level
    
  - platform: ha_ip_monitor
    name: "攻击来源国家分布"
    entity_id: sensor.attack_source_countries
```

---

## 🚀 开发计划

### 📅 开发里程碑

#### **Phase 1: 基础框架 (第1-2周)**
- [ ] **Week 1**
  - [ ] 创建HACS集成基础结构
  - [ ] 实现配置向导界面
  - [ ] VPS连接测试功能
  - [ ] 基础传感器框架

- [ ] **Week 2**  
  - [ ] VPS监控脚本开发
  - [ ] 自动部署功能
  - [ ] 基础UI界面
  - [ ] 数据通信测试

#### **Phase 2: 核心功能 (第3-4周)**
- [ ] **Week 3**
  - [ ] 威胁监控仪表盘
  - [ ] 实时威胁列表
  - [ ] 基础IP封锁功能
  - [ ] 攻击统计展示

- [ ] **Week 4**
  - [ ] 批量IP管理
  - [ ] 紧急锁定功能
  - [ ] 基础通知系统
  - [ ] 错误处理机制

#### **Phase 3: 增强功能 (第5-6周)**
- [ ] **Week 5**
  - [ ] 威胁情报集成
  - [ ] 地理位置分析
  - [ ] 高级可视化图表
  - [ ] 性能优化

- [ ] **Week 6**
  - [ ] 多渠道通知
  - [ ] 自动化规则引擎
  - [ ] 用户文档完善
  - [ ] 发布准备

### 🎯 MVP发布目标

#### **核心功能清单**
- ✅ 一键安装和配置
- ✅ VPS安全状态监控
- ✅ 攻击IP实时显示
- ✅ 单击封锁IP功能
- ✅ 基础攻击统计
- ✅ 移动端友好界面

#### **成功指标**
- 安装成功率 > 95%
- 配置完成时间 < 5分钟  
- 威胁检测准确率 > 98%
- 用户满意度 > 4.5/5.0

---

## 🔒 安全考虑

### 🛡️ 安全设计原则

#### **1. 最小权限原则**
```yaml
VPS权限控制:
  - 监控脚本使用非root用户运行
  - 仅授权必要的系统命令
  - API接口限制访问IP范围
  - 定期轮换API密钥
```

#### **2. 数据传输安全**
```yaml
通信加密:
  - 所有API调用使用HTTPS
  - 通过WireGuard加密隧道传输
  - API Token动态生成
  - 敏感数据不落地存储
```

#### **3. 访问控制**
```yaml
认证机制:
  - HA用户权限验证
  - VPS API Token验证
  - IP白名单限制
  - 操作日志记录
```

### ⚠️ 风险评估

| 风险项目 | 风险等级 | 缓解措施 |
|---------|----------|----------|
| **VPS连接泄露** | 中等 | WireGuard加密 + IP限制 |
| **误封重要IP** | 中等 | 白名单保护 + 操作确认 |
| **API滥用** | 低等 | 频率限制 + Token轮换 |
| **配置错误** | 低等 | 向导验证 + 回滚机制 |

---

## 📈 商业化考虑

### 💰 盈利模式

#### **开源免费版**
- ✅ 基础监控功能
- ✅ 单VPS支持
- ✅ 社区技术支持
- ✅ 基础威胁检测

#### **Pro专业版 ($29/年)**
- ✅ 多VPS集群监控
- ✅ 高级威胁情报
- ✅ 自定义自动化规则
- ✅ 优先技术支持
- ✅ 专业报告功能

#### **Enterprise企业版 ($99/年)**
- ✅ 无限VPS数量
- ✅ API开放接口
- ✅ 企业级SLA支持
- ✅ 定制化开发
- ✅ 私有部署支持

### 📊 市场定位
- **目标市场**: Home Assistant用户生态 (100万+用户)
- **细分市场**: 家庭服务器安全需求 (10万+用户)
- **竞争优势**: HA原生集成 + 一键部署 + 专业功能

---

## 🤝 项目协作

### 👥 开发团队
- **项目负责人**: Cody (产品设计 + 需求定义)
- **AI开发助手**: Claude (代码开发 + 技术实现)
- **目标用户**: HA社区用户 (测试反馈)

### 📋 协作方式
- **开发工具**: VSCode + Claude Code
- **版本控制**: Git + GitHub
- **项目管理**: GitHub Issues + Projects
- **文档维护**: Markdown + GitHub Wiki

### 🔄 开发流程
1. **需求确认** → **技术设计** → **代码开发**
2. **单元测试** → **集成测试** → **用户测试**  
3. **代码审查** → **性能优化** → **发布部署**

---

## 📞 联系方式

### 🔗 项目仓库
- **GitHub**: `https://github.com/cody/HA_IP_Monitor`
- **HACS**: 待发布到HACS社区商店
- **文档**: 项目Wiki + README.md

### 📧 反馈渠道
- **Issues**: GitHub Issues系统
- **讨论**: GitHub Discussions
- **邮件**: 项目维护者邮箱
- **社区**: Home Assistant中文社区

---

## ✅ 下一步行动

### 🎯 立即行动项
1. **[ ] 在VSCode中初始化项目结构**
2. **[ ] 创建基础的manifest.json和__init__.py** 
3. **[ ] 设计config_flow.py配置向导**
4. **[ ] 开发VPS连接测试功能**
5. **[ ] 创建第一个传感器原型**

### 🚀 本周目标
- **完成基础项目框架搭建**
- **实现VPS连接和基础数据获取**
- **创建简单的HA传感器显示**
- **验证技术可行性**

### 📅 下周计划
- **开发威胁监控仪表盘**
- **实现IP封锁功能**
- **添加批量操作界面**
- **完善错误处理机制**

---

## 🔄 开发工作流程

### 📋 每日工作流程 (重要！)

#### 🌅 开始工作前
1. **阅读核心文档** (按顺序):
   - 📖 `README.md` - 了解项目全局
   - 📊 `PROJECT_STATUS.md` - 了解当前状态
   - 🤝 `HANDOFF_YYYY-MM-DD_vX.X.md` - 了解今日任务

2. **确认开发目标**
   - 明确今日优先级
   - 理解任务依赖关系

#### 💻 开发过程中
- 遵循 `.claude/PROJECT_RULES.md` 中的代码规范
- 代码注释使用日语
- 用户交互使用中文
- 频繁commit代码

#### 🌙 工作结束前 (必须完成！)
1. ✅ 更新 `PROJECT_STATUS.md` (修改记录、文件状态、下一步计划)
2. ✅ 更新 `README.md` (更新日志部分)
3. ✅ 删除旧的交接文件
4. ✅ 创建新的交接文件 `HANDOFF_<明天日期>_v<新版本>.md`
5. ✅ Git commit 并 push

### 📁 重要文件说明

| 文件 | 作用 | 更新频率 |
|-----|------|---------|
| `PROJECT_STATUS.md` | 项目总体状态追踪 | 每次修改代码后 |
| `HANDOFF_YYYY-MM-DD_vX.X.md` | 每日工作交接 | 每天结束前 |
| `.claude/PROJECT_RULES.md` | Claude AI工作规则 | 偶尔更新 |
| `README.md` | 项目需求和架构 | 重大变更时 |

---

## 📝 更新日志

### Version 0.4.0-dev - 服务功能实现 (2025-11-13)
- ✅ 创建服务定义 (`services.yaml`)
  - block_ip: 封锁指定IP地址
  - unblock_ip: 解除IP封锁
  - emergency_lockdown: 紧急安全锁定
- ✅ 实现服务注册和处理 (`__init__.py`)
  - 异步服务处理函数
  - voluptuous参数验证schema
  - 完整的错误处理和日志记录
  - 服务调用后自动刷新数据
- ✅ 添加多语言服务翻译
  - 英文 (en.json)
  - 中文 (zh-Hans.json)
  - 日语 (ja.json)

**功能完成度**:
- Phase 1: 基础架构 ✅ 100%
- Phase 2: 数据层 ✅ 100%
- Phase 3: VPS API业务逻辑 ✅ 100%
- Phase 4: 服务功能 ✅ 100%
- Phase 5: 集成测试 ⏳ 待开始

**代码统计**:
- Python: ~2,900行 (+750行)
- YAML: 45行 (新增)
- JSON翻译: ~350行
- 配置文件: 4个
- 文档文件: 8个

### Version 0.3.0-dev - VPS API业务逻辑 (2025-11-13)
- ✅ 实现系统状态监控 (`vps_monitor_api.py`)
  - CPU/内存/磁盘使用率监控
  - auth.log日志解析引擎
  - SSH/VPN攻击检测 (正则表达式)
- ✅ 实现UFW防火墙集成
  - IP封禁/解封功能
  - 防火墙状态查询
  - 命令注入防护
- ✅ 实现威胁分析引擎
  - 威胁等级自动计算
  - 攻击IP排序和统计
  - 封禁状态追踪
- ✅ 实现高级功能
  - 白名单管理 (GET/POST/DELETE)
  - IP详细信息查询
  - 紧急锁定功能
  - 30秒缓存机制

**API端点** (8个):
- `GET /health` - 健康检查
- `GET /api/status` - 系统状态
- `GET /api/threats` - 威胁列表
- `POST /api/block` - 封禁IP
- `POST /api/unblock` - 解封IP
- `GET/POST/DELETE /api/whitelist` - 白名单管理
- `POST /api/ip_info` - IP详情
- `POST /api/emergency` - 紧急锁定

**代码统计**:
- Python: ~2,150行 (+550行)
- VPS API: 729行 (核心文件)

### Version 0.2.0-dev - 数据层实现 (2025-11-13)
- ✅ 实现数据协调器 (`coordinator.py`)
  - 每60秒自动从VPS获取数据
  - 完善的错误处理和重试机制
  - 实现API请求封装和响应处理
  - 实现IP封锁/解封功能接口
- ✅ 实现传感器平台 (`sensor.py`)
  - 5个传感器实体 (系统状态、威胁等级、攻击统计等)
  - CoordinatorEntity集成
  - 动态图标和状态显示
- ✅ 更新集成入口 (`__init__.py`)
- ✅ 更新依赖配置 (`manifest.json`)

**代码统计**:
- Python: ~1,600行 (+100行)

### Version 0.1.0-dev - 基础框架搭建 (2025-11-12)
- ✅ 完成项目需求定义
- ✅ 确定技术架构方案
- ✅ 设计用户界面规格
- ✅ 创建项目基础框架 (17个文件)
- ✅ 实现Home Assistant集成核心文件
- ✅ 实现VPS监控API框架
- ✅ 实现自定义Lovelace卡片框架
- ✅ 建立项目管理和交接机制

**代码统计**:
- Python: ~1,500行
- JavaScript: ~400行
- 配置文件: 3个
- 文档文件: 8个

---

**项目创建时间**: 2025年11月12日
**文档版本**: 0.4.0-dev
**最后更新**: 2025年11月13日
**项目状态**: ✅ **Phase 4 服务功能完成 - 准备部署测试**

> 💡 **备注**: 本文档将随着项目进展持续更新，所有重要变更将记录在更新日志中。
>
> 📖 **开发者必读**:
> - [PROJECT_STATUS.md](.claude/PROJECT_STATUS.md) - 项目总体状态
> - [HANDOFF_2025-11-13_v0.3.md](HANDOFF_2025-11-13_v0.3.md) - 最新交接文件
> - [.claude/PROJECT_RULES.md](.claude/PROJECT_RULES.md) - AI工作规则
> - [remote_scripts/README.md](remote_scripts/README.md) - VPS部署文档

---

## 🚀 快速部署指南

### 当前功能状态
- ✅ Phase 1-4: 核心功能已完成 (100%)
- ⏳ Phase 5: 部署测试进行中

### VPS端部署 (5分钟)
```bash
# 1. 克隆项目
git clone https://github.com/MorinoC/HA_IP_Monitor.git
cd HA_IP_Monitor/remote_scripts

# 2. 运行自动安装脚本
chmod +x installer.sh
sudo ./installer.sh

# 安装完成后会显示API Token，请保存
```

### Home Assistant端部署
```bash
# 方式1: 手动复制
cp -r custom_components/ha_ip_monitor /config/custom_components/
ha core restart

# 方式2: 通过HACS (未来支持)
# HACS → 集成 → 搜索 "HA IP Monitor"
```

### 配置集成
1. 进入 **设置 → 设备与服务 → 添加集成**
2. 搜索 **"HA IP Monitor"**
3. 输入VPS信息和API Token
4. 完成配置，查看5个传感器

### 使用服务功能
```yaml
# 封禁IP
service: ha_ip_monitor.block_ip
data:
  ip_address: "192.168.1.100"

# 解封IP
service: ha_ip_monitor.unblock_ip
data:
  ip_address: "192.168.1.100"

# 紧急锁定
service: ha_ip_monitor.emergency_lockdown
data:
  reason: "检测到大规模攻击"
```

详细部署文档请查看: [remote_scripts/README.md](remote_scripts/README.md)

---

## 🔖 附录

### 📚 相关文档链接
- [Home Assistant开发文档](https://developers.home-assistant.io/)
- [HACS集成指南](https://hacs.xyz/docs/publish/integration)
- [VPS安全配置文档](./vps_server_config.md)
- [Home Server架构文档](./homeServer_config_V2.0.md)

### 🛠️ 开发工具清单
- **VSCode**: 主要IDE
- **Claude Code**: AI开发助手
- **Python 3.9+**: 后端开发语言
- **JavaScript/TypeScript**: 前端开发语言
- **Home Assistant Core**: 目标平台

### 📊 技术参数
- **最低HA版本**: 2023.11.0+
- **Python依赖**: `requests`, `paramiko`, `geoip2`
- **前端依赖**: `lit-element`, `@material/mwc-*`
- **网络要求**: WireGuard或直接网络连接到VPS
