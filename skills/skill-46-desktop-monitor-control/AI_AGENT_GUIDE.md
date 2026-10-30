# AI 桌面代理 - 认知自动化指南

## 🤖 这是什么？

**AI 桌面代理**是基础桌面控制之上的智能层，能够**理解**您的需求并自主找出实现方法。

与需要精确指令的基础自动化不同，AI 代理：
- **理解自然语言**（"在画图中画一只猫"）
- **自动规划步骤**
- **自主执行**
- **适应**屏幕上的内容

---

## 🎯 它能做什么？

### ✅ 自主绘图
```python
from skills.desktop_control.ai_agent import AIDesktopAgent

agent = AIDesktopAgent()

# 只需描述您想要的！
agent.execute_task("在画图中画一个圆")
agent.execute_task("在 MS Paint 中画一颗星星")
agent.execute_task("画一座有太阳的房子")
```

**它的工作原理：**
1. 打开 MS Paint
2. 选择铅笔工具
3. 找出如何绘制请求的形状
4. 自主绘制
5. 截图保存结果

### ✅ 自主文本输入
```python
# 它会找出在哪里输入
agent.execute_task("在记事本中输入 'Hello World'")
agent.execute_task("写一封感谢邮件")
```

**它的工作原理：**
1. 打开记事本（或找到活动的文本编辑器）
2. 自然地输入文本
3. 如需要则格式化

### ✅ 自主应用程序控制
```python
# 它知道如何打开应用
agent.execute_task("打开计算器")
agent.execute_task("启动 Microsoft Paint")
agent.execute_task("打开文件资源管理器")
```

### ✅ 自主游戏（高级）
```python
# 它会尝试玩游戏！
agent.execute_task("帮我玩纸牌接龙")
agent.execute_task("玩扫雷")
```

**它的工作原理：**
1. 分析游戏屏幕
2. 检测游戏状态（卡牌、地雷等）
3. 决定最佳移动
4. 执行移动
5. 重复直到获胜/失败

---

## 🏗️ 工作原理

### 架构

```
用户请求（"画一只猫"）
    ↓
自然语言理解
    ↓
任务规划（分步计划）
    ↓
步骤执行循环：
    - 观察屏幕（计算机视觉）
    - 决定动作（AI 推理）
    - 执行动作（桌面控制）
    - 验证结果
    ↓
任务完成！
```

### 关键组件

1. **任务规划器** - 将高级任务分解为步骤
2. **视觉系统** - 理解屏幕内容（截图、OCR、对象检测）
3. **推理引擎** - 决定下一步做什么
4. **动作执行器** - 执行实际的鼠标/键盘动作
5. **反馈循环** - 验证操作成功

---

## 📋 支持的任务（当前）

### 第 1 层：完全自动化 ✅

| 任务模式 | 示例 | 状态 |
|---------|------|------|
| 在 Paint 中绘制形状 | "画一个圆" | ✅ 工作中 |
| 基本文本输入 | "输入 Hello" | ✅ 工作中 |
| 启动应用程序 | "打开 Paint" | ✅ 工作中 |

### 第 2 层：部分自动化 🔨

| 任务模式 | 示例 | 状态 |
|---------|------|------|
| 表单填充 | "填写这个表单" | 🔨 进行中 |
| 文件操作 | "复制这些文件" | 🔨 进行中 |
| 网页导航 | "在 Google 上查找" | 🔨 计划中 |

### 第 3 层：实验性 🧪

| 任务模式 | 示例 | 状态 |
|---------|------|------|
| 游戏玩耍 | "玩纸牌接龙" | 🧪 实验性 |
| 图像编辑 | "调整这张照片大小" | 🧪 计划中 |
| 代码编辑 | "修复这个 bug" | 🧪 研究中 |

---

## 🎨 示例：在 Paint 中绘图

### 简单请求
```python
agent = AIDesktopAgent()
result = agent.execute_task("在画图中画一个圆")

# 检查结果
print(f"状态: {result['status']}")
print(f"执行的步骤: {len(result['steps'])}")
```

### 幕后发生的事情

**1. 规划阶段：**
```
生成的计划：
  步骤 1：启动 MS Paint
  步骤 2：等待 2 秒让 Paint 加载
  步骤 3：激活 Paint 窗口
  步骤 4：选择铅笔工具（按 'P'）
  步骤 5：在画布中心画圆
  步骤 6：截图结果
```

**2. 执行阶段：**
```
[✓] 通过 Win+R → mspaint 启动 Paint
[✓] 等待 2.0 秒
[✓] 激活窗口 "Paint"
[✓] 按 'P' 选择铅笔
[✓] 用 72 个点画圆
[✓] 截图已保存：drawing_result.png
```

**3. 结果：**
```python
{
    "task": "在画图中画一个圆",
    "status": "completed",
    "success": True,
    "steps": [... 6 个步骤 ...],
    "screenshots": [... 6 张截图 ...],
}
```

---

## 🎮 示例：游戏玩耍

```python
agent = AIDesktopAgent()

# 玩一个简单的游戏
result = agent.execute_task("帮我玩纸牌接龙")
```

### 游戏玩耍循环

```
1. 分析屏幕 → 检测卡牌、位置
2. 识别有效移动 → 找到合法的操作
3. 评估移动 → 哪个最好？
4. 执行移动 → 点击并拖动卡牌
5. 重复直到游戏结束
```

### 游戏特定智能

代理可以学习以下模式：
- **纸牌接龙**：卡牌堆叠规则、花色匹配
- **扫雷**：概率计算、安全点击
- **2048**：方块合并策略
- **国际象棋**（如果集成引擎）：移动评估

---

## 🧠 增强 AI

### 添加应用程序知识

```python
# 在 ai_agent.py 中，添加到 app_knowledge：

self.app_knowledge = {
    "photoshop": {
        "name": "Adobe Photoshop",
        "launch_command": "photoshop",
        "common_actions": {
            "new_layer": {"hotkey": ["ctrl", "shift", "n"]},
            "brush_tool": {"hotkey": ["b"]},
            "eraser": {"hotkey": ["e"]},
        }
    }
}
```

### 添加自定义任务模式

```python
# 添加自定义规划方法
def _plan_photo_edit(self, task: str) -> List[Dict]:
    """照片编辑任务规划。"""
    return [
        {"type": "launch_app", "app": "photoshop"},
        {"type": "wait", "duration": 3.0},
        {"type": "open_file", "path": extracted_path},
        {"type": "apply_filter", "filter": extracted_filter},
        {"type": "save_file"},
    ]
```

---

## 🔥 高级：视觉 + 推理

### 屏幕分析

代理可以分析截图以：
- **检测 UI 元素**（按钮、文本字段、菜单）
- **阅读文本**（OCR 用于标签、说明）
- **识别对象**（图标、图像、游戏棋子）
- **理解布局**（事物在哪里）

```python
# 分析屏幕上的内容
analysis = agent._analyze_screen()

print(analysis)
# 输出：
# {
#     "active_window": "无标题 - Paint",
#     "mouse_position": (640, 480),
#     "detected_elements": [...],
#     "text_found": [...],
# }
```

### 与 OpenClaw LLM 集成

```python
# 未来：使用 OpenClaw 的 LLM 进行推理
agent = AIDesktopAgent(llm_client=openclaw_llm)

# 代理现在可以：
# - 对复杂任务进行推理
# - 更好地理解上下文
# - 规划更复杂的工作流
# - 从反馈中学习
```

---

## 🛠️ 为您的需求扩展

### 为新应用添加支持

1. **识别应用**
2. **记录常见操作**
3. **添加到知识库**
4. **创建规划方法**

示例：添加 Excel 支持

```python
# 步骤 1：添加到 app_knowledge
"excel": {
    "name": "Microsoft Excel",
    "launch_command": "excel",
    "common_actions": {
        "new_sheet": {"hotkey": ["shift", "f11"]},
        "sum_formula": {"action": "type", "text": "=SUM()"},
    }
}

# 步骤 2：创建规划器
def _plan_excel_task(self, task: str) -> List[Dict]:
    return [
        {"type": "launch_app", "app": "excel"},
        {"type": "wait", "duration": 2.0},
        # ... 特定的 Excel 步骤
    ]

# 步骤 3：挂钩到主规划器
if "excel" in task_lower or "spreadsheet" in task_lower:
    return self._plan_excel_task(task)
```

---

## 🎯 现实世界用例

### 1. 自动表单填充
```python
agent.execute_task("用我的简历数据填写求职申请")
```

### 2. 批量图像处理
```python
agent.execute_task("将此文件夹中的所有图像调整为 800x600")
```

### 3. 社交媒体发布
```python
agent.execute_task("将此图片发布到 Instagram，配文'美丽的日落'")
```

### 4. 数据录入
```python
agent.execute_task("将此 PDF 中的数据复制到 Excel 电子表格")
```

### 5. 测试
```python
agent.execute_task("使用无效凭据测试登录表单")
```

---

## ⚙️ 配置

### 启用/禁用故障保护
```python
# 安全模式（默认）
agent = AIDesktopAgent(failsafe=True)

# 快速模式（无故障保护）
agent = AIDesktopAgent(failsafe=False)
```

### 设置最大步骤数
```python
# 防止无限循环
result = agent.execute_task("玩游戏", max_steps=100)
```

### 访问操作历史
```python
# 查看代理做了什么
print(agent.action_history)
```

---

## 🐛 调试

### 查看分步执行
```python
result = agent.execute_task("在 Paint 中画一颗星星")

for i, step in enumerate(result['steps'], 1):
    print(f"步骤 {i}: {step['step']['description']}")
    print(f"  成功: {step['success']}")
    if 'error' in step:
        print(f"  错误: {step['error']}")
```

### 查看截图
```python
# 每个步骤捕获前后截图
for screenshot_pair in result['screenshots']:
    before = screenshot_pair['before']
    after = screenshot_pair['after']
    
    # 显示或保存以供分析
    before.save(f"step_{screenshot_pair['step']}_before.png")
    after.save(f"step_{screenshot_pair['step']}_after.png")
```

---

## 🚀 未来增强

计划的功能：

- [ ] **计算机视觉**：OCR、对象检测、UI 元素识别
- [ ] **LLM 集成**：使用 OpenClaw LLM 进行自然语言理解
- [ ] **学习**：记住成功的模式，随时间改进
- [ ] **多应用工作流**："从 Chrome 获取数据并放入 Excel"
- [ ] **语音控制**："Alexa，在 Paint 中画一只猫"
- [ ] **自主调试**：自动修复错误
- [ ] **游戏 AI**：用于游戏玩耍的强化学习
- [ ] **网页自动化**：具有理解力的完整浏览器控制

---

## 📚 完整 API

### 主要方法

```python
# 执行任务
result = agent.execute_task(task: str, max_steps: int = 50)

# 分析屏幕
analysis = agent._analyze_screen()

# 手动模式：执行单个步骤
step = {"type": "launch_app", "app": "paint"}
result = agent._execute_step(step)
```

### 结果结构

```python
{
    "task": str,                    # 原始任务
    "status": str,                  # "completed"、"failed"、"error"
    "success": bool,                # 整体成功
    "steps": List[Dict],            # 执行的所有步骤
    "screenshots": List[Dict],      # 前后截图
    "failed_at_step": int,          # 如果失败，哪个步骤
    "error": str,                   # 失败时的错误消息
}
```

---

**🦞 为 OpenClaw 构建 - 桌面自动化的未来！**
