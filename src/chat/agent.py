import json
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich import print

from chat.tools import shell, read, write, tools
from prompt.system_prompt import get_system_prompt
from prompt.skills import get_skills_list


logger = logging.getLogger(__name__)


load_dotenv()
api_key = os.getenv('API_KEY')
model_name = os.getenv('MODEL_NAME')
base_url = os.getenv('BASE_URL')

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)


def send_messages(messages: list):
    """发送一次API请求，返回原始响应对象"""
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools
    )
    logger.debug(response.model_dump_json(indent=2))
    return response


def execute_tool(tool_call):
    """根据 tool_call 执行对应的工具，返回结果字符串"""
    func_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if func_name == 'shell':
        command = arguments['command']
        print(f"[dim]执行命令: {command}[/dim]")
        return shell(command)

    elif func_name == 'write':
        target_file = arguments['target_file']
        content = arguments['content']
        print(f"[dim]写入文件: {target_file}[/dim]")
        return write(target_file, content)

    elif func_name == 'read':
        target_file = arguments['target_file']
        print(f"[dim]读取文件: {target_file}[/dim]")
        return read(target_file)

    else:
        logger.warning(f'未知工具调用: {func_name}')
        return f'Error: unknown tool {func_name}'


def process_turn(messages: list):
    """
    发送消息并自动处理所有工具调用循环，直到模型返回文本回复。
    成功时返回最终响应对象（choices[0].message.content 可用）。
    失败时返回 None。
    """
    messages = messages.copy()
    logger.debug(f'消息列表（无system）: {messages}')

    # 每次调用时获取最新的系统提示词和技能列表
    system_content = get_system_prompt() + get_skills_list()
    messages.insert(0, {"role": "system", "content": system_content})

    response = send_messages(messages)

    if not response.choices:
        print("[red]API 调用失败[/red]")
        logger.error(f'API调用失败，响应: {response}')
        return None

    while response.choices[0].message.tool_calls:
        # 将模型的工具调用消息加入历史
        messages.append(response.choices[0].message.model_dump(exclude_none=True))

        for tool_call in response.choices[0].message.tool_calls:
            tool_output = execute_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_output
            })

        response = send_messages(messages)

        if not response.choices:
            print("[red]API 调用失败[/red]")
            logger.error(f'API调用失败，响应: {response}')
            return None

    logger.debug(f'模型响应: {response}')

    messages.append(response.choices[0].message.model_dump(exclude_none=True))

    logger.debug(f'变量messages[1:]: {messages[1:]}')

    return messages[1:]