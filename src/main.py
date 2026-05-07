import os
import logging
from pathlib import Path
from rich import print
from rich.markdown import Markdown

from chat import process_turn
from prompt.summary import summary


models = [
    ['Deepseek-ai/deepseek-v4-pro', 'Deepseek V4 Pro'],
    ['Qwen/Qwen3.5-397B-A17B', 'Qwen 3.5']
]


log_dir = Path("./logs")
log_dir.mkdir(parents=True, exist_ok=True)

# 1. 根 logger 设为 WARNING（所有第三方库默认）
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.setLevel(logging.WARNING)

# 2. 自己的代码包设为 DEBUG（按包名前缀）
for module_prefix in ['chat', 'prompt']:  # 你的代码包名
    logging.getLogger(module_prefix).setLevel(logging.DEBUG)

# 3. 文件 handler：记录 DEBUG 及以上
file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

# 4. 只给自己的代码包添加 handler（避免第三方日志进来）
for module_prefix in ['chat', 'prompt']:
    logging.getLogger(module_prefix).addHandler(file_handler)

# 5. 获取当前模块 logger
logger = logging.getLogger(__name__)


# ---------- 初始化消息列表 ----------
messages = []

os.system('cls' if os.name == 'nt' else 'clear')


# ---------- 主循环 ----------
while True:
    print('─' * os.get_terminal_size().columns)
    print('[bold yellow]>[/bold yellow]  ', end='')
    user_input = input('')
    print('─' * os.get_terminal_size().columns)

    if not user_input:
        continue

    if user_input[0] == '/':
        command = user_input[1:].lower()

        if command == 'quit':
            # print("再见！")
            logger.info('退出软件')
            break

        elif command == 'summary':
            if not messages:
                print("[red]没有可压缩的对话[/red]")
                continue
            print(f"[dim]压缩对话中...")

            messages.append({'role': 'system', 'content': summary})
            logger.debug(f'Messages: {messages}')

            # 调用封装好的函数，自动处理工具调用
            response = process_turn(messages)

            if response is None:
                continue
            else:
                messages = response

            # 清空消息，只保留系统提示 + 摘要内容
            messages.clear()
            messages.append({
                'role': 'system',
                'content': f'此前对话：\n{response.choices[0].message.content}'
            })
            print(f"[dim]压缩对话成功[/dim]")

        elif command == 'model' or command == 'models':
            print(f"请选择模型：")
            for i in range(len(models)):
                print(f'{i+1} {models[i][1]}')

        elif command == 'new_model':
            pass

        else:
            pass
        

    else:
        messages.append({'role': 'user', 'content': user_input})

        response = process_turn(messages)

        if response is None:
                continue
        else:
            messages = response
            if messages[-1]['role'] == 'assistant':
                print(Markdown(messages[-1]['content']))
                # if response.usage:
                #     print(f'[dim]本次消耗token {response.usage.total_tokens}[/dim]')
    
    print()