import os
from pathlib import Path
import subprocess


tools = [
    {
        "type": "function",
        "function": {
            "name": "shell",
            "description": f"在终端运行命令。用户操作系统：。在Windows中尽量使用Powershell（command: powershell -Command \"...\"）。",
            "parameters": {
                "properties": {
                    "command": {
                        "description": "要执行的终端命令，不要换行。",
                        "type": "string"
                    },
                    "timeout": {
                        "description": "超时（秒）。",
                        "type": "integer"
                    }
                },
                "required": ["command"],
                "type": "object"
            }
        }
    },
    {
        "type": "function",
        'function': {
            'name': 'write',
            "description": "写文件。",
            "parameters": {
                "properties": {
                    "target_file": {
                        "description": "目标文件的绝对路径。",
                        "type": "string"
                    },
                    "content": {
                        "description": "文件内容。",
                        "type": "string"
                    },
                },
                "required": ["target_file",'content'],
                "type": "object"
            }
        }
    },
    {
        "type": "function",
        'function': {
            'name': 'read',
            "description": "读文件。",
            "parameters": {
                "properties": {
                    "target_file": {
                        "description": "目标文件的绝对路径。",
                        "type": "string"
                    }
                },
                "required": ["target_file"],
                "type": "object"
            }
        }
    }
]


def shell(command, timeout=30):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.stdout:
            return result.stdout
        elif result.stderr:
            return f"错误: {result.stderr}"
        else:
            return f"命令执行完成，退出码: {result.returncode}"
    except subprocess.TimeoutExpired:
        return "命令执行超时"
    except Exception as e:
        return f"执行命令时出错: {str(e)}"
    

def write(target_file, content):
    """写入文件"""
    try:
        Path(target_file).write_text(content, encoding='utf-8')
        return "写入文件完成"
    except Exception as e:
        return f"写入文件时出错: {str(e)}"
        
    

def read(target_file):
    """读取文件"""
    try:
        result = Path(target_file).read_text(encoding='utf-8')
        return result
    except Exception as e:
        return f"写入文件时出错: {str(e)}"