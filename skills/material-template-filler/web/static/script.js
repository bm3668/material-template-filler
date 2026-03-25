// 材料模板填充 Web 应用 - 前端交互逻辑

// 状态管理
let state = {
    templatePath: null,
    templateFilename: null,
    inputPath: null,
    inputFilename: null,
    content: '',
    selectedHistoryFile: null,
    currentTab: 'input',
    generateMindmap: false,
    mermaidContent: '',
    mindmapTab: 'auto',
    isProcessing: false
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setupUploadHandlers();
});

// 设置上传处理器
function setupUploadHandlers() {
    // 模板上传
    const templateUploadArea = document.getElementById('template-upload-area');
    const templateInput = document.getElementById('template-input');
    
    templateUploadArea.addEventListener('click', () => templateInput.click());
    templateInput.addEventListener('change', handleTemplateUpload);
    
    setupDragDrop(templateUploadArea, (file) => uploadTemplateFile(file));
    
    // 项目说明文件上传
    const inputUploadArea = document.getElementById('input-upload-area');
    const inputUploadInput = document.getElementById('input-upload-input');
    
    inputUploadArea.addEventListener('click', () => inputUploadInput.click());
    inputUploadInput.addEventListener('change', handleInputUpload);
    
    setupDragDrop(inputUploadArea, (file) => uploadInputFile(file));
    
    // 回车发送（Ctrl+Enter 换行）
    const contentInput = document.getElementById('content-input');
    contentInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.ctrlKey && state.currentTab === 'input') {
            // 可选：自动开始填充
            // e.preventDefault();
            // startFill();
        }
    });
}

// 设置拖拽上传
function setupDragDrop(element, callback) {
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.style.background = '#e8f5e9';
    });
    
    element.addEventListener('dragleave', () => {
        element.style.background = '';
    });
    
    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.style.background = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            callback(files[0]);
        }
    });
}

// 切换标签页
function switchTab(tab) {
    state.currentTab = tab;
    
    // 更新标签样式
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    document.querySelector(`.tab:nth-child(${tab === 'input' ? 1 : tab === 'upload' ? 2 : 3})`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    checkFillButton();
}

// 处理模板上传
function handleTemplateUpload(e) {
    const file = e.target.files[0];
    if (file) uploadTemplateFile(file);
}

// 上传模板文件
async function uploadTemplateFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload/template', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.templatePath = data.path;
            state.templateFilename = data.filename;
            
            document.getElementById('template-filename').textContent = data.filename;
            document.getElementById('template-path').textContent = data.path;
            document.getElementById('template-info').style.display = 'flex';
            document.getElementById('template-upload-area').style.display = 'none';
            
            checkFillButton();
        } else {
            alert('上传失败：' + data.error);
        }
    } catch (error) {
        console.error('上传错误:', error);
        alert('上传失败，请重试');
    }
}

// 移除模板
function removeTemplate() {
    state.templatePath = null;
    state.templateFilename = null;
    
    document.getElementById('template-info').style.display = 'none';
    document.getElementById('template-upload-area').style.display = 'block';
    document.getElementById('template-input').value = '';
    
    checkFillButton();
}

// 处理项目说明文件上传
function handleInputUpload(e) {
    const file = e.target.files[0];
    if (file) uploadInputFile(file);
}

// 上传项目说明文件
async function uploadInputFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload/input', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.inputPath = data.path;
            state.inputFilename = data.filename;
            state.selectedHistoryFile = null;
            
            document.getElementById('input-filename').textContent = data.filename;
            document.getElementById('input-file-info').style.display = 'flex';
            document.getElementById('input-upload-area').style.display = 'none';
            
            // 切换到上传标签
            switchTab('upload');
            
            checkFillButton();
            
            // 启用思维导图生成按钮
            const btn = document.getElementById('btn-generate-mindmap-upload');
            if (btn) {
                btn.disabled = false;
            }
        } else {
            alert('上传失败：' + data.error);
        }
    } catch (error) {
        console.error('上传错误:', error);
        alert('上传失败，请重试');
    }
}

// 移除项目说明文件
function removeInputFile() {
    state.inputPath = null;
    state.inputFilename = null;
    
    document.getElementById('input-file-info').style.display = 'none';
    document.getElementById('input-upload-area').style.display = 'block';
    document.getElementById('input-upload-input').value = '';
    
    checkFillButton();
}

// 加载历史文件列表
async function loadHistory() {
    try {
        const response = await fetch('/api/list-inputs');
        const data = await response.json();
        
        const listEl = document.getElementById('history-list');
        
        if (data.files.length === 0) {
            listEl.innerHTML = '<p class="empty-text">暂无历史文件</p>';
            return;
        }
        
        listEl.innerHTML = data.files.map(f => `
            <div class="file-item ${state.selectedHistoryFile === f.path ? 'selected' : ''}" 
                 onclick="selectHistoryFile('${f.path}', '${f.name}')">
                <div class="file-info-content">
                    <span class="file-name">📄 ${f.name}</span>
                    <span class="file-meta">${f.size} bytes · ${f.mtime}</span>
                </div>
                <span class="select-indicator">${state.selectedHistoryFile === f.path ? '✓' : ''}</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('加载历史失败:', error);
    }
}

// 选择历史文件
function selectHistoryFile(path, name) {
    state.selectedHistoryFile = path;
    state.inputPath = path;
    state.inputFilename = name;
    state.content = '';
    
    // 更新 UI
    document.querySelectorAll('.file-item').forEach(item => {
        item.classList.remove('selected');
        const indicator = item.querySelector('.select-indicator');
        if (indicator) indicator.textContent = '';
    });
    
    const selectedItem = Array.from(document.querySelectorAll('.file-item'))
        .find(item => item.querySelector('.file-name')?.textContent.includes(name));
    if (selectedItem) {
        selectedItem.classList.add('selected');
        selectedItem.querySelector('.select-indicator').textContent = '✓';
    }
    
    checkFillButton();
    
    // 启用思维导图生成按钮（历史文件标签页）
    const btn = document.getElementById('btn-generate-mindmap-history');
    if (btn) {
        btn.disabled = false;
    }
}

// 检查填充按钮状态
function checkFillButton() {
    const btn = document.getElementById('btn-fill');
    const hasTemplate = state.templatePath !== null;
    
    let hasContent = false;
    if (state.currentTab === 'input') {
        hasContent = state.content.trim().length > 0;
    } else if (state.currentTab === 'upload') {
        hasContent = state.inputPath !== null;
    } else if (state.currentTab === 'history') {
        hasContent = state.selectedHistoryFile !== null;
    }
    
    btn.disabled = !(hasTemplate && hasContent) || state.isProcessing;
}

// 监听内容输入
document.getElementById('content-input')?.addEventListener('input', (e) => {
    state.content = e.target.value;
    checkFillButton();
    
    // 启用/禁用思维导图按钮
    const btn = document.getElementById('btn-generate-mindmap');
    if (btn) {
        btn.disabled = !state.content.trim() || state.isProcessing;
    }
});

// 开始填充
async function startFill() {
    if (!state.templatePath || state.isProcessing) return;
    
    state.isProcessing = true;
    checkFillButton();
    
    // 显示状态
    document.getElementById('status-section').style.display = 'block';
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('log-output').textContent = '';
    
    try {
        const payload = {
            template_path: state.templatePath,
            content: state.currentTab === 'input' ? state.content : '',
            input_path: (state.currentTab === 'upload' || state.currentTab === 'history') ? state.inputPath : null,
            // 思维导图选项
            generate_mindmap: state.generateMindmap,
            mermaid_content: state.mindmapTab === 'custom' ? 
                document.getElementById('mermaid-input')?.value : 
                state.mermaidContent
        };
        
        const response = await fetch('/api/fill', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 隐藏状态，显示结果
            document.getElementById('status-section').style.display = 'none';
            document.getElementById('result-section').style.display = 'block';
            
            // 设置下载链接
            const downloadLink = document.getElementById('download-link');
            downloadLink.href = `/api/download/${data.output_filename}`;
            
            // 设置结果信息
            document.getElementById('result-filename').textContent = data.output_filename;
            document.getElementById('result-time').textContent = new Date().toLocaleString('zh-CN');
            
            // 存储报告内容
            window.currentReport = data.report_content;
            
            // 保存状态用于对话改进
            state.lastOutputFile = data.output_filename;
            state.originalContent = state.content;
            
            if (data.log) {
                document.getElementById('log-output').textContent = data.log;
            }
        } else {
            throw new Error(data.error || '填充失败');
        }
    } catch (error) {
        console.error('填充错误:', error);
        document.getElementById('status-section').style.display = 'none';
        alert('填充失败：' + error.message);
    } finally {
        state.isProcessing = false;
        checkFillButton();
    }
}

// 显示报告
function showReport() {
    if (!window.currentReport) {
        alert('没有报告内容');
        return;
    }
    
    const modal = document.getElementById('report-modal');
    const content = document.getElementById('report-content');
    
    // 将 Markdown 转换为 HTML
    content.innerHTML = `<pre>${escapeHtml(window.currentReport)}</pre>`;
    
    modal.style.display = 'flex';
}

// 关闭报告
function closeReport() {
    document.getElementById('report-modal').style.display = 'none';
}

// 工具函数：HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 点击模态框外部关闭
window.addEventListener('click', (e) => {
    const modal = document.getElementById('report-modal');
    if (e.target === modal) {
        closeReport();
    }
});

// 页面加载时加载历史文件列表
loadHistory();

// ========== 思维导图相关功能 ==========

// 从当前内容生成思维导图
async function generateMindmapFromContent() {
    const content = document.getElementById('content-input').value;
    if (!content.trim()) {
        alert('请先输入项目内容');
        return;
    }
    
    await generateMindmap(content);
}

// 从上传的文件生成思维导图
async function generateMindmapFromFile() {
    if (!state.inputPath) {
        alert('请先上传文件');
        return;
    }
    
    const btn = document.getElementById('btn-generate-mindmap-upload');
    const originalText = btn.textContent;
    btn.textContent = '⏳ 生成中...';
    btn.disabled = true;
    
    try {
        // 读取文件内容
        const response = await fetch('/api/read-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: state.inputPath })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await generateMindmap(data.content, btn, originalText);
        } else {
            alert('读取文件失败：' + data.error);
            btn.textContent = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('读取文件失败:', error);
        alert('读取文件失败，请重试');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// 从历史文件生成思维导图
async function generateMindmapFromHistory() {
    if (!state.selectedHistoryFile) {
        alert('请先选择历史文件');
        return;
    }
    
    const btn = document.getElementById('btn-generate-mindmap-history');
    const originalText = btn.textContent;
    btn.textContent = '⏳ 生成中...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/api/read-file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: state.selectedHistoryFile })
        });
        
        const data = await response.json();
        
        if (data.success) {
            await generateMindmap(data.content, btn, originalText);
        } else {
            alert('读取文件失败：' + data.error);
            btn.textContent = originalText;
            btn.disabled = false;
        }
    } catch (error) {
        console.error('读取文件失败:', error);
        alert('读取文件失败，请重试');
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

// 生成思维导图（通用函数）
async function generateMindmap(content, btn = null, originalText = '🎨 生成思维导图预览') {
    // 如果没有传入按钮，使用默认按钮
    if (!btn) {
        btn = document.getElementById('btn-generate-mindmap');
        if (!btn) {
            btn = document.getElementById('btn-generate-mindmap-upload');
        }
        if (!btn) {
            btn = document.getElementById('btn-generate-mindmap-history');
        }
        originalText = btn ? btn.textContent : '🎨 生成思维导图预览';
    }
    
    if (btn) {
        btn.textContent = '⏳ 生成中...';
        btn.disabled = true;
    }
    
    try {
        const response = await fetch('/api/generate-mindmap', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: content })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 存储 Mermaid 代码
            state.mermaidContent = data.mermaid;
            
            // 显示预览模态框
            showMindmapModal(data.mermaid);
        } else {
            alert('生成失败：' + data.error);
        }
    } catch (error) {
        console.error('生成思维导图失败:', error);
        alert('生成失败，请重试');
    } finally {
        if (btn) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

// 显示思维导图预览模态框
function showMindmapModal(mermaidCode) {
    document.getElementById('mindmap-mermaid-code').textContent = mermaidCode;
    document.getElementById('mindmap-modal').style.display = 'flex';
}

// 关闭思维导图模态框
function closeMindmapModal() {
    document.getElementById('mindmap-modal').style.display = 'none';
}

// 复制 Mermaid 代码
function copyMermaidCode() {
    const code = document.getElementById('mindmap-mermaid-code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        alert('✅ Mermaid 代码已复制到剪贴板！');
    }).catch(err => {
        alert('复制失败，请手动复制');
    });
}

// 点击模态框外部关闭
window.addEventListener('click', (e) => {
    const reportModal = document.getElementById('report-modal');
    const mindmapModal = document.getElementById('mindmap-modal');
    const chatModal = document.getElementById('chat-modal');
    
    if (e.target === reportModal) {
        closeReport();
    }
    if (e.target === mindmapModal) {
        closeMindmapModal();
    }
    if (e.target === chatModal) {
        closeChatModal();
    }
});

// ========== 对话改进功能 ==========

// 打开对话模态框
function openChatModal() {
    document.getElementById('chat-modal').style.display = 'flex';
    // 聚焦到输入框
    setTimeout(() => {
        document.getElementById('chat-input').focus();
    }, 100);
}

// 关闭对话模态框
function closeChatModal() {
    document.getElementById('chat-modal').style.display = 'none';
}

// 发送对话消息
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    const sendBtn = document.getElementById('btn-send-chat');
    sendBtn.disabled = true;
    
    // 添加用户消息到聊天窗口
    addChatMessage(message, 'user');
    
    // 清空输入框
    input.value = '';
    
    // 显示正在输入提示
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch('/api/chat-improve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                last_output: state.lastOutputFile,
                original_content: state.originalContent
            })
        });
        
        // 移除加载提示
        removeLoadingMessage(loadingId);
        
        const data = await response.json();
        
        if (data.success) {
            // 添加 AI 回复
            addChatMessage(data.response, 'bot');
            
            // 如果有新版本文档，更新下载链接
            if (data.new_version_file) {
                state.lastOutputFile = data.new_version_file;
                document.getElementById('download-link').href = `/api/download/${data.new_version_file}`;
                document.getElementById('download-link').textContent = `📥 下载最新版本 (${data.version || 'v2'})`;
                
                // 添加系统消息
                addChatMessage(`✅ 已生成新版本文档：<strong>${data.new_version_file}</strong>`, 'bot');
            }
        } else {
            addChatMessage('❌ 处理失败：' + data.error, 'bot');
        }
    } catch (error) {
        console.error('对话失败:', error);
        removeLoadingMessage(loadingId);
        addChatMessage('❌ 连接失败，请重试', 'bot');
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

// 添加聊天消息
function addChatMessage(content, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const timestamp = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-meta">${type === 'user' ? '你' : '助手'} · ${timestamp}</div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    
    // 滚动到底部
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加加载提示
function addLoadingMessage() {
    const messagesContainer = document.getElementById('chat-messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot-message';
    loadingDiv.id = 'loading-' + Date.now();
    
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(loadingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return loadingDiv.id;
}

// 移除加载提示
function removeLoadingMessage(loadingId) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
        loadingEl.remove();
    }
}

// 检查填充按钮状态（更新版）
function checkFillButton() {
    const btn = document.getElementById('btn-fill');
    const hasTemplate = state.templatePath !== null;
    const hasContent = (state.currentTab === 'input' && state.content.trim()) ||
                       (state.currentTab === 'upload' && state.inputPath) ||
                       (state.currentTab === 'history' && state.selectedHistoryFile);
    
    btn.disabled = !(hasTemplate && hasContent) || state.isProcessing;
}
