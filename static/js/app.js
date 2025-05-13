document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const questionForm = document.getElementById('question-form');
    const questionInput = document.getElementById('question-input');
    const loadingOverlay = document.getElementById('loading-overlay');

    // 检查API服务器是否可用
    checkApiHealth();

    // 定期检查API健康状态
    setInterval(checkApiHealth, 30000); // 每30秒检查一次

    // 处理用户提交问题
    questionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const question = questionInput.value.trim();
        if (!question) return;
        
        // 添加用户消息到聊天区域
        addMessage('user', question);
        
        // 清空输入框
        questionInput.value = '';
        
        // 显示加载动画
        showLoading(true);
        
        try {
            console.log('开始发送请求到API');
            
            // 检查是否是直接图像生成请求
            const imageGenPatterns = ['画一只', '画一个', '生成图像', '制作图片'];
            const isImageRequest = imageGenPatterns.some(pattern => question.includes(pattern));
            
            // 确定使用哪个API
            const apiUrl = '/api/ask';
            console.log(`使用API: ${apiUrl}, 是否为图像请求: ${isImageRequest}`);
            
            // 发送请求到后端API
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question })
            });
            
            console.log('API响应状态:', response.status);
            
            if (!response.ok) {
                throw new Error('请求失败: ' + response.status);
            }
            
            const data = await response.json();
            console.log('API响应数据:', data);
            
            // 处理回复
            if (data.error) {
                console.error('API返回错误:', data.error);
                addMessage('ai', `抱歉，发生了错误: ${data.error}`);
            } else {
                console.log('成功获取回答');
                // 添加AI回答
                const messageElement = addMessage('ai', data.answer || '抱歉，我暂时无法生成回答。');
                
                // 如果返回了图像URL，添加图像
                if (data.image_url) {
                    console.log('添加图像:', data.image_url);
                    addImageToMessage(messageElement, data.image_url);
                }
                
                // 如果返回了文档信息，可以选择性地显示
                if (data.documents && data.documents.length > 0) {
                    console.log('参考文档:', data.documents);
                    // 这里可以添加代码显示参考的文档内容
                }
            }
        } catch (error) {
            console.error('请求出错:', error);
            addMessage('ai', `抱歉，服务器连接失败: ${error.message || '未知错误'}`);
        } finally {
            // 隐藏加载动画
            showLoading(false);
            
            // 滚动到底部
            scrollToBottom();
        }
    });
    
    // 检查API健康状态
    async function checkApiHealth() {
        try {
            console.log('检查API健康状态...');
            const response = await fetch('/api/health');
            if (response.ok) {
                const data = await response.json();
                console.log('API健康状态:', data);
                // 可以在这里更新UI元素表明服务器状态
                document.querySelector('.loading-overlay p').textContent = '正在思考中...';
            } else {
                console.error('API健康检查失败:', response.status);
                document.querySelector('.loading-overlay p').textContent = '服务器连接不稳定...';
            }
        } catch (error) {
            console.error('API健康检查异常:', error);
        }
    }
    
    // 添加消息到聊天区域
    function addMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<p>${formatText(content)}</p>`;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // 滚动到底部
        scrollToBottom();
        
        return contentDiv;
    }
    
    // 格式化文本，支持简单的Markdown
    function formatText(text) {
        if (!text) return '暂无回答';
        
        // 将连续的换行符转换为段落
        text = text.replace(/\n{2,}/g, '</p><p>');
        
        // 将单个换行符转换为<br>
        text = text.replace(/\n/g, '<br>');
        
        // 支持基本的Markdown语法（粗体、斜体等）
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // 粗体
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>'); // 斜体
        
        // 支持列表
        if (text.includes('- ')) {
            const listItems = text.split('- ').filter(item => item.trim());
            if (listItems.length > 0) {
                text = '<ul>' + listItems.map(item => `<li>${item.trim()}</li>`).join('') + '</ul>';
            }
        }
        
        return text;
    }
    
    // 添加图像到消息
    function addImageToMessage(messageElement, imageUrl) {
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = '生成的图像';
        img.loading = 'lazy';
        
        // 添加加载动画
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        
        // 图像加载完成后显示
        img.onload = () => {
            img.style.opacity = '1';
            scrollToBottom();
        };
        
        // 添加失败处理
        img.onerror = () => {
            console.error('图像加载失败:', imageUrl);
            const errorMsg = document.createElement('p');
            errorMsg.className = 'image-error';
            errorMsg.innerHTML = '图像加载失败。<a href="' + imageUrl + '" target="_blank">点击此处</a>尝试直接查看。';
            messageElement.appendChild(errorMsg);
        };
        
        messageElement.appendChild(img);
    }
    
    // 控制加载动画的显示/隐藏
    function showLoading(show) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }
    
    // 滚动到聊天区域底部
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 添加快捷按钮
    addQuickButtons();
    
    function addQuickButtons() {
        const quickButtons = [
            { text: '体测项目', query: '青岛理工大学体测有哪些项目？' },
            { text: '综合素质评价', query: '学生综合素质评价办法是什么？' },
            { text: '画一只鸟', query: '画一只鸟' }
        ];
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'quick-buttons';
        
        quickButtons.forEach(button => {
            const btn = document.createElement('button');
            btn.className = 'quick-button';
            btn.textContent = button.text;
            btn.onclick = () => {
                questionInput.value = button.query;
                questionForm.dispatchEvent(new Event('submit'));
            };
            buttonContainer.appendChild(btn);
        });
        
        // 在聊天输入框上方插入按钮
        const chatContainer = document.querySelector('.chat-container');
        chatContainer.insertBefore(buttonContainer, document.querySelector('.chat-input'));
    }
    
    // 焦点到输入框
    questionInput.focus();
}); 