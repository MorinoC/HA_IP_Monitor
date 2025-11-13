# 🚀 新AI快速启动提示词

> **复制下面的文字，粘贴给新的AI对话即可**

---

```
你好！我接手了一个Home Assistant集成开发项目，需要你帮我继续开发。

项目名称: HA IP Monitor (VPS安全监控集成)
当前版本: v0.3.0-dev
项目路径: C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor

请按以下步骤开始：

1. 首先阅读这3个文件了解项目：
   - .claude/QUICK_START.md (工作流程)
   - .claude/PROJECT_STATUS.md (项目进度)
   - HANDOFF_2025-11-13_v0.3.md (今天要做什么)

2. 当前项目状态：
   - ✅ Phase 1: 基础架构完成
   - ✅ Phase 2: 数据层完成
   - ✅ Phase 3: VPS API业务逻辑完成
   - ⏳ Phase 4: 服务功能 ← 现在要做这个
   - ⏳ Phase 5: 集成测试

3. 下一步任务（Phase 4）：
   实现Home Assistant服务功能，让用户可以通过UI手动封禁/解封IP

   需要做3件事：
   - 创建 custom_components/ha_ip_monitor/services.yaml
   - 更新 custom_components/ha_ip_monitor/__init__.py 注册服务
   - 添加服务翻译到 translations/*.json

   详细说明和代码示例在 HANDOFF_2025-11-13_v0.3.md 第277-323行

4. 重要规则：
   - 代码注释用日语（// システムステータスを取得）
   - 用户消息用中文（logger.info("正在连接...")）
   - 频繁git commit
   - 工作结束前更新HANDOFF文档

请告诉我你读完文档后的理解，然后我们开始Phase 4的开发。
```

---

## 📝 备选简化版（如果AI上下文有限）

```
你好！继续开发HA IP Monitor项目。

项目路径: C:\Users\CodyZhang\Desktop\app\HA_IP_Monitor
当前进度: Phase 3完成，需要做Phase 4

请先读取并总结这个文件的内容：
HANDOFF_2025-11-13_v0.3.md

读完后告诉我：
1. 项目是做什么的
2. 已经完成了什么
3. 下一步要做什么

然后我们开始Phase 4开发。
```

---

## 🎯 预期AI回复

正常情况下，新AI会回复类似：

```
我已经读取了项目文档，理解如下：

**项目概况**:
HA IP Monitor是一个Home Assistant HACS集成，用于监控VPS服务器的安全状况...

**已完成**:
- Phase 1-3: 基础架构、数据层、VPS API业务逻辑
- 核心功能：5个传感器、数据协调器、VPS API（8个端点）

**下一步任务** (Phase 4):
实现3个HA服务：block_ip、unblock_ip、emergency_lockdown
需要创建services.yaml并在__init__.py中注册

我准备好开始开发了，需要我先创建services.yaml吗？
```

---

## ⚠️ 如果AI说看不到文件

使用这个提示：

```
请使用Read工具读取以下文件：

1. HANDOFF_2025-11-13_v0.3.md (特别是第273-323行)
2. .claude/PROJECT_STATUS.md
3. .claude/QUICK_START.md

然后总结项目状态和下一步任务。
```

---

**使用方法**:
1. 复制上面的"新AI快速启动提示词"内容
2. 粘贴到新的Claude对话中
3. 等待AI读取文档并确认理解
4. 开始Phase 4开发

**最后更新**: 2025-11-13 19:40
