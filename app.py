from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import urllib.parse
import json5
import traceback
import logging
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')

# 修改为绝对路径以确保静态文件能被找到
static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')
CORS(app)  # 启用跨域资源共享

# 打印静态文件夹路径以便调试
print(f"静态文件夹路径: {static_folder}")

# 注册图像生成工具
@register_tool('my_image_gen')
class MyImageGen(BaseTool):
    description = 'AI 绘画（图像生成）服务，输入文本描述，返回基于文本信息绘制的图像 URL。'
    parameters = [{
        'name': 'prompt',
        'type': 'string',
        'description': '期望的图像内容的详细描述',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            logger.info(f"图像生成工具被调用，参数: {params}")
            prompt_data = json5.loads(params)
            prompt = prompt_data['prompt']
            logger.info(f"原始提示词: {prompt}")
            
            # 确保中文提示词被正确编码
            prompt = urllib.parse.quote(prompt)
            logger.info(f"编码后提示词: {prompt}")
            
            # 生成图像URL
            image_url = f'https://image.pollinations.ai/prompt/{prompt}'
            logger.info(f"生成图像URL: {image_url}")
            
            result = json5.dumps({'image_url': image_url}, ensure_ascii=False)
            logger.info(f"返回结果: {result}")
            return result
        except Exception as e:
            logger.error(f"图像生成出错: {str(e)}")
            logger.error(traceback.format_exc())
            return json5.dumps({'error': f'图像生成失败: {str(e)}'}, ensure_ascii=False)

# LLM配置
llm_cfg = {
    'model': 'deepseek-v3',
    'model_server': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'api_key': 'sk-882e296067b744289acf27e6e20f3ec0',
    'generate_cfg': {
        'top_p': 0.8
    }
}

# 系统指令
system_instruction = '''你是青岛理工大学的智能助手。
你可以：
1. 回答关于青岛理工大学的问题，基于加载的文档内容
2. 如果用户要求生成图像（例如包含"画"、"生成图像"、"制作图片"等词语的请求），请使用my_image_gen工具生成相关图像
3. 必要时使用code_interpreter工具执行代码

请用中文回复用户，保持回答友好、准确。如果需要生成图像，请立即调用my_image_gen工具，不要拒绝。'''

# 工具列表
tools = ['my_image_gen', 'code_interpreter']

# 加载文档
def load_documents():
    file_dir = os.path.join('./', 'docs')
    files = []
    if os.path.exists(file_dir):
        for file in os.listdir(file_dir):
            file_path = os.path.join(file_dir, file)
            if os.path.isfile(file_path):
                files.append(file_path)
    return files

# 创建助手实例
bot = None  # 我们将在主函数中初始化它

@app.route('/')
def index():
    logger.info("访问首页")
    return send_from_directory(static_folder, 'index.html')

# 添加静态文件直接访问路由
@app.route('/css/<path:filename>')
def serve_css(filename):
    logger.info(f"请求CSS文件: {filename}")
    return send_from_directory(os.path.join(static_folder, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    logger.info(f"请求JS文件: {filename}")
    return send_from_directory(os.path.join(static_folder, 'js'), filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    logger.info(f"请求图像文件: {filename}")
    return send_from_directory(os.path.join(static_folder, 'images'), filename)

# 添加直接图像生成API
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': '提示词不能为空'}), 400
            
        logger.info(f"直接图像生成API被调用，提示词: {prompt}")
        
        # 调用图像生成工具
        image_generator = MyImageGen()
        params = json5.dumps({'prompt': prompt}, ensure_ascii=False)
        result = image_generator.call(params)
        
        # 解析结果
        response_data = json5.loads(result)
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"直接图像生成出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'图像生成失败: {str(e)}'}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    logger.info("接收到API请求")
    logger.info(f"请求头: {request.headers}")
    
    try:
        data = request.json
        logger.info(f"请求数据: {data}")
        
        query = data.get('question', '')
        logger.info(f"用户问题: {query}")
        
        if not query:
            logger.warning("问题为空")
            return jsonify({'error': '问题不能为空'}), 400
        
        # 检查是否是图像生成请求
        if any(keyword in query for keyword in ['画一只', '画一个', '生成图像', '制作图片']):
            logger.info("检测到图像生成请求")
            # 提取提示词
            prompt = query
            if '画一只' in query:
                prompt = query.split('画一只')[-1]
            elif '画一个' in query:
                prompt = query.split('画一个')[-1]
            elif '生成图像' in query and ':' in query:
                prompt = query.split(':')[-1]
            elif '生成图像' in query:
                prompt = query.replace('生成图像', '')
            
            # 调用图像生成工具
            image_generator = MyImageGen()
            params = json5.dumps({'prompt': prompt.strip()}, ensure_ascii=False)
            result = image_generator.call(params)
            response_data = json5.loads(result)
            
            if 'error' in response_data:
                return jsonify({'error': response_data['error']}), 500
                
            # 返回成功结果
            return jsonify({
                'answer': f'我已经按照你的要求画了{prompt}，希望你喜欢！',
                'image_url': response_data['image_url']
            })
        
        # 创建消息
        messages = [{'role': 'user', 'content': query}]
        
        # 获取回答
        final_response = None
        retrieved_docs = []
        
        # 检查是否有文档检索器
        logger.info("检查文档检索器")
        if hasattr(bot, 'retriever') and bot.retriever:
            docs = bot.retriever.retrieve(query)
            if docs:
                for doc in docs:
                    retrieved_docs.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata
                    })
                logger.info(f"检索到 {len(retrieved_docs)} 个文档片段")
            else:
                logger.info("没有检索到相关文档")
        
        # 运行助手获取回答
        logger.info("开始生成回答")
        try:
            for response in bot.run(messages=messages):
                final_response = response
                logger.info("获取到回答")
        except Exception as e:
            logger.error(f"生成回答时出错: {e}")
            logger.error(traceback.format_exc())
            return jsonify({'error': f'生成回答时出错: {str(e)}'}), 500
        
        # 提取回答内容
        if final_response:
            logger.info(f"最终回答: {final_response}")
        else:
            logger.error("未获取到回答")
            
        result = {
            'answer': final_response[0]['content'] if final_response and len(final_response) > 0 and 'content' in final_response[0] else '',
            'documents': retrieved_docs
        }
        
        # 检查是否有工具调用
        if final_response and len(final_response) > 0 and 'tool_calls' in final_response[0]:
            tool_calls = final_response[0]['tool_calls']
            for tool_call in tool_calls:
                if tool_call['name'] == 'my_image_gen' and 'response' in tool_call:
                    try:
                        image_data = json5.loads(tool_call['response'])
                        if 'image_url' in image_data:
                            result['image_url'] = image_data['image_url']
                            logger.info(f"生成图像URL: {image_data['image_url']}")
                    except Exception as e:
                        logger.error(f"解析图像URL时出错: {e}")
        
        logger.info(f"返回结果: {result}")
        return jsonify(result)
    
    except Exception as e:
        error_message = f'处理请求时出错: {str(e)}'
        logger.error(error_message)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_message}), 500

# 添加一个简单的健康检查端点
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

# 使用不同的端口
if __name__ == '__main__':
    print("正在加载文档...")
    docs = load_documents()
    print(f"已加载 {len(docs)} 个文档")
    
    # 初始化助手
    try:
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction,
            function_list=tools,
            files=docs
        )
        print("助手初始化成功")
    except Exception as e:
        print(f"助手初始化失败: {e}")
        traceback.print_exc()
        
    app.run(debug=True, port=5001, threaded=True) 