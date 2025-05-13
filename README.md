# 青岛理工大学智能助手

基于RAG（Qwen-Agent）的智能助手应用，旨在为青岛理工大学的师生提供信息查询和智能服务。

> **注意**：当前的知识库文件尚不完整，只包含少量示例文档，仅供功能演示之用。实际部署时需要添加更多相关文档以提供全面的信息服务。

## 功能特点

- 查询学校相关信息（体育测试、学生评价办法等）
- 基于文档的智能问答（RAG技术）
- AI图像生成功能（支持中文提示词）
- 简洁美观的Web界面
- 快捷按钮，一键提问常见问题

## 项目现状

- **知识库**：目前仅包含几个示例文档，需要扩充
- **问答功能**：基本完成，可以回答关于文档内容的问题
- **图像生成**：已完善实现，支持通过关键词直接生成图像
- **Web界面**：已实现响应式设计，适配不同设备

## 安装步骤

1. 克隆或下载本项目到本地

2. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

3. 安装RAG和Code Interpreter支持
   ```bash
   pip install "qwen-agent[rag]"
   pip install "qwen-agent[code_interpreter]"
   ```

## 使用前配置

> **重要**：在运行应用前，您需要在`app.py`和`qwen-agent-multi-files.py`（如果使用）中配置有效的API密钥。

1. 打开`app.py`文件，找到以下代码段：
   ```python
   llm_cfg = {
       'model': 'deepseek-v3',
       'model_server': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
       'api_key': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',  # 替换为您的API密钥
       'generate_cfg': {
           'top_p': 0.8
       }
   }
   ```

2. 将`'api_key': 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'`中的占位符替换为您的实际API密钥。

3. 保存文件后再启动应用。

## 使用方法

1. 确保您在项目根目录下有一个`docs`文件夹，并在其中放入相关文档（PDF、Word等）
   > 当前示例文档仅作演示用途，实际使用时请添加更多学校相关文档

2. 启动Web服务
   ```bash
   python app.py
   ```
   
   或者指定特定Python环境（例如在Windows上）：
   ```bash
   & <Python路径>/python.exe app.py
   ```

3. 打开浏览器，访问以下地址：
   ```
   http://127.0.0.1:5001
   ```

4. 在对话框中输入您的问题，按回车键或点击发送按钮即可
   - 可以使用自然语言查询文档内容
   - 可以使用"画一只..."或"生成图像..."来触发图像生成
   - 可以点击快捷按钮直接发送预设问题

## 环境要求

- Python 3.9+
- Flask 2.3.3+
- qwen-agent 0.0.22+（需安装RAG和code_interpreter扩展）
- 支持PDF和Word文档的解析（需要pdfminer和python-docx）

## 目录结构

```
├── app.py                 # 主要应用程序（Web版本）
├── qwen-agent-multi-files.py  # 命令行版本（仅供参考，不再积极维护）
├── requirements.txt       # 项目依赖
├── docs/                  # 文档目录（当前为示例文档）
│   ├── 信息与控制工程学院2024年推免工作实施细则.pdf
│   ├── 关于评选2024年度国家奖助学金的通知.doc
│   ├── 青岛理工大学学生综合素质评价办法（修订）.pdf
│   └── 青理工校发〔2022〕63号青岛理工大学学生体质健康测试工作实施办法.pdf
└── static/                # 前端文件
    ├── index.html         # 主页面
    ├── css/               # 样式文件
    │   └── style.css
    ├── js/                # JavaScript文件
    │   └── app.js
    └── images/            # 图片资源
        └── logo.png       # 学校LOGO
```

## 关于命令行版本

`qwen-agent-multi-files.py`是本项目的命令行版本，主要用途：
- 在不需要Web界面的环境中快速测试
- 作为学习Qwen-Agent基本用法的参考示例
- 便于故障排查和开发调试

该版本不再积极维护，建议主要使用`app.py`（Web版本）。

## 注意事项

- 如果遇到文档编码问题，请确保文档使用UTF-8编码
- 服务启动时可能需要几分钟时间来加载和处理文档
- 请确保API密钥配置正确，没有有效API密钥将无法运行
- 在不同Python环境中运行可能需要重新安装依赖
- 图像生成功能依赖于外部服务，需要网络连接

## 已知问题

- 某些Word文档可能存在解析编码问题
- 图像生成可能因网络原因偶尔失败
- 首次启动时文档加载较慢

## 未来计划

- [ ] 扩充知识库，添加更多学校相关文档
- [ ] 改进文档解析，支持更多格式
- [ ] 添加用户认证和会话管理
- [ ] 支持语音输入和输出
- [ ] 实现更多校园服务集成

## 扩展与定制

- 可以通过修改`static/css/style.css`文件来定制界面样式
- 可以通过修改`app.py`中的系统指令来调整AI助手的行为
- 可以在`static/js/app.js`中添加更多快捷按钮