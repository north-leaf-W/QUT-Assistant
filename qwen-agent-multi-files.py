import pprint
import urllib.parse
import json5
import sys
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool


# 步骤 1（可选）：添加一个名为 `my_image_gen` 的自定义工具。
@register_tool('my_image_gen')
class MyImageGen(BaseTool):
    # `description` 用于告诉智能体该工具的功能。
    description = 'AI 绘画（图像生成）服务，输入文本描述，返回基于文本信息绘制的图像 URL。'
    # `parameters` 告诉智能体该工具有哪些输入参数。
    parameters = [{
        'name': 'prompt',
        'type': 'string',
        'description': '期望的图像内容的详细描述',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        # `params` 是由 LLM 智能体生成的参数。
        prompt = json5.loads(params)['prompt']
        prompt = urllib.parse.quote(prompt)
        print(f"\n正在生成图像，提示词: {prompt}")
        result = json5.dumps(
            {'image_url': f'https://image.pollinations.ai/prompt/{prompt}'},
            ensure_ascii=False)
        print(f"生成图像URL: {json5.loads(result)['image_url']}")
        return result


# 步骤 2：配置您所使用的 LLM。
llm_cfg = {
    # 使用 DashScope 提供的模型服务：
    'model': 'qwen-max',
    'model_server': 'dashscope',
    'api_key': 'sk-882e296067b744289acf27e6e20f3ec0',
    'generate_cfg': {
        'top_p': 0.8
    }
}

llm_cfg = {
    # 使用 DashScope 提供的模型服务：
    'model': 'deepseek-v3',
    'model_server': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'api_key': 'sk-882e296067b744289acf27e6e20f3ec0',
    'generate_cfg': {
        'top_p': 0.8
    }
}

# 步骤 3：创建一个智能体。这里我们以 `Assistant` 智能体为例，它能够使用工具并读取文件。
system_instruction = '''你是青岛理工大学的智能助手。
你可以：
1. 回答关于青岛理工大学的问题，基于加载的文档内容
2. 如果用户明确要求，可以使用my_image_gen工具生成相关图像
3. 必要时使用code_interpreter工具执行代码

请用中文回复用户，保持回答友好、准确。'''
tools = ['my_image_gen', 'code_interpreter']  # `code_interpreter` 是框架自带的工具，用于执行代码。
import os
# 获取文件夹下所有文件
file_dir = os.path.join('./', 'docs')
files = []
if os.path.exists(file_dir):
    # 遍历目录下的所有文件
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if os.path.isfile(file_path):  # 确保是文件而不是目录
            files.append(file_path)
print('files=', files)

bot = Assistant(llm=llm_cfg,
                system_message=system_instruction,
                function_list=tools,
                files=files)

# 步骤 4：作为聊天机器人运行智能体。
messages = []  # 这里储存聊天历史。
# 从控制台获取用户输入
query = input("请输入您的问题: ")
# 将用户请求添加到聊天历史。
messages.append({'role': 'user', 'content': query})
response = []
current_index = 0

try:
    for response in bot.run(messages=messages):
        if current_index == 0:
            # 尝试获取并打印召回的文档内容
            if hasattr(bot, 'retriever') and bot.retriever:
                print("\n===== 召回的文档内容 =====")
                retrieved_docs = bot.retriever.retrieve(query)
                if retrieved_docs:
                    for i, doc in enumerate(retrieved_docs):
                        print(f"\n文档片段 {i+1}:")
                        print(f"内容: {doc.page_content}")
                        print(f"元数据: {doc.metadata}")
                else:
                    print("没有召回任何文档内容")
                print("===========================\n")

        # 确保输出当前响应部分
        if len(response) > 0 and 'content' in response[0]:
            current_response = response[0]['content'][current_index:]
            current_index = len(response[0]['content'])
            print(current_response, end='', flush=True)  # 使用flush参数确保立即输出
        
        # 输出工具调用信息
        if len(response) > 0 and 'tool_calls' in response[0]:
            print("\n===== 工具调用 =====")
            for tool_call in response[0]['tool_calls']:
                print(f"调用工具: {tool_call['name']}")
                print(f"参数: {tool_call['parameters']}")
                if 'response' in tool_call:
                    print(f"响应: {tool_call['response']}")
            print("=====================\n")
            
    # 完成后输出完整响应内容
    if response and len(response) > 0:
        print("\n\n===== 完整响应 =====")
        print(response[0]['content'])
        print("=====================")
        
except Exception as e:
    print(f"\n执行过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

# 将机器人的回应添加到聊天历史。
#messages.extend(response)

