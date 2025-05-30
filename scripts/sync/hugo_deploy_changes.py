#!/usr/bin/env python3
#coding=utf-8

import argparse
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

GIT_HASH_LENGTH = 40
HASH_FILE_SUFFIX = ".hash"
# 获取脚本绝对路径
SCRIPT_DIR_PATH = Path(__file__).resolve().parent


# 配置日志格式
class SingleRunFileHandler(logging.FileHandler):
    """单次运行日志处理器，每次覆盖旧日志"""
    def __init__(self, filename):
        super().__init__(filename, mode='w', encoding='utf-8')


# 配置单次运行日志系统
log_format = '%(asctime)s | %(levelname)-8s | %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 文件处理器（单次运行模式）
file_handler = SingleRunFileHandler(SCRIPT_DIR_PATH / 'latest_hugo_depoly_changes.log')
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
# 创建日志对象
logger = logging.getLogger(__name__)



class GitSyncError(Exception):
    """自定义异常基类"""
    pass

class GitOperationError(GitSyncError):
    """Git操作异常"""
    pass

class FileOperationError(GitSyncError):
    """文件操作异常"""
    pass

class SecurityError(GitSyncError):
    """安全相关异常"""
    pass

class DeploymentError(GitSyncError):
    """部署过程异常"""
    pass

def deploy_changes(repo_path: Path) -> None:
    """
    执行部署流程：
    1. 清理旧构建文件
    2. 生成静态资源
    3. 重载Nginx配置
    """
    logger.info("启动部署流程")
    commands = [
        {
            "cmd": ["rm", "-rf", "public"],
            "desc": "清理旧构建文件",
            "error": "清理失败"
        },
        {
            "cmd": ["/usr/local/bin/hugo", "--source", str(repo_path)],
            "desc": "生成静态资源",
            "error": "Hugo构建失败"
        },
        {
            "cmd": ["sudo", "/usr/sbin/nginx", "-s", "reload"],
            "desc": "重载Nginx配置",
            "error": "Nginx重载失败"
        }
    ]

    try:
        for step in commands:
            logger.info(step["desc"] + "...")
            result = subprocess.run(
                step["cmd"],
                cwd=repo_path if step["cmd"][0] != "sudo" else None,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"命令输出: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        error_msg = f"{step['error']}: {e.stderr.strip()}"
        logger.error(error_msg)
        logger.debug(f"失败命令: {' '.join(e.cmd)}")
        raise DeploymentError(error_msg) from e
    except FileNotFoundError as e:
        error_msg = f"命令不存在: {e.filename}"
        logger.error(error_msg)
        raise DeploymentError(error_msg) from e
    logger.info("部署流程完成")


def validate_directory(path: str) -> Path:
    """验证并返回安全的Path对象"""
    try:
        dir_path = Path(path).resolve(strict=True)
        
        # 安全限制：禁止相对路径穿越
        if ".." in dir_path.parts:
            raise SecurityError("路径包含非法相对路径")
            
        if not dir_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {dir_path}")
            
        # 权限检查
        if not os.access(dir_path, os.R_OK | os.W_OK):
            raise PermissionError(f"目录权限不足: {dir_path}")
            
        # 验证是否为Git仓库
        if not (dir_path / ".git").exists():
            raise ValueError("目标目录不是Git仓库")
            
        return dir_path
    except FileNotFoundError as e:
        raise FileNotFoundError(f"目录不存在: {path}") from e

def get_git_head_hash(repo_path: Path) -> str:
    """获取当前分支最新提交hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()
        if len(commit_hash) != GIT_HASH_LENGTH:
            raise ValueError(f"无效的Git提交哈希长度: {len(commit_hash)}")
        return commit_hash
    except subprocess.CalledProcessError as e:
        error_msg = f"Git命令执行失败: {e.stderr.strip()}"
        logger.error(error_msg)
        raise GitOperationError(error_msg) from e

def get_hash_file_path(repo_path: Path) -> Path:
    """生成当前目录下的hash文件路径"""
    return SCRIPT_DIR_PATH / f"{repo_path.name}{HASH_FILE_SUFFIX}"

def read_hash_file(file_path: Path) -> Optional[str]:
    """安全读取存储的hash值"""
    try:
        if not file_path.exists():
            return None
            
        with open(file_path, 'r') as f:
            content = f.read().strip()
            if len(content) != GIT_HASH_LENGTH:
                logger.warning("文件中的哈希值格式无效")
                return None
            return content
    except IOError as e:
        error_msg = f"文件读取失败: {file_path} - {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e

def write_hash_file(file_path: Path, commit_hash: str) -> None:
    """安全写入hash值"""
    try:
        with open(file_path, 'w') as f:
            f.write(commit_hash)
        logger.debug(f"成功写入哈希文件: {file_path}")
    except IOError as e:
        error_msg = f"文件写入失败: {file_path} - {str(e)}"
        logger.error(error_msg)
        raise FileOperationError(error_msg) from e

def git_pull(repo_path: Path) -> None:
    """执行git pull（超时结束）"""
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        logger.info(f"Git pull成功: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Git pull失败: {e.stderr.strip()}"
        logger.error(error_msg)
        raise GitOperationError(error_msg) from e

def process_repository(target_dir: str) -> None:
    """主处理流程"""
    try:
        repo_path = validate_directory(target_dir)
        logger.info(f"处理仓库: {repo_path}")
        
        logger.info("正在同步远端内容...")
        git_pull(repo_path)

        hash_file = get_hash_file_path(repo_path)
        logger.debug(f"使用的哈希文件: {hash_file}")
        
        current_hash = get_git_head_hash(repo_path)
        logger.info(f"当前提交哈希: {current_hash[:8]}...")
        
        stored_hash = read_hash_file(hash_file)
        logger.info(f"存储的哈希: {stored_hash[:8] + '...' if stored_hash else '无'}")
        
        if current_hash != stored_hash:
            logger.info("检测到哈希变化，更新当前哈希记录文件...")
            write_hash_file(hash_file, current_hash)
            logger.info("仓库和哈希文件更新完成")

            # 部署流程
            try:
                deploy_changes(repo_path)
            except DeploymentError:
                logger.warning("部署流程失败，已保留最新提交哈希")
        else:
            logger.info("提交哈希一致，无需操作")
            
    except GitSyncError as e:
        logger.error(f"处理失败: {str(e)}")
        raise
    except Exception as e:
        logger.critical(f"未预期的错误: {str(e)}", exc_info=True)
        raise GitSyncError("严重错误发生") from e

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="Git仓库哈希同步工具",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'directory',
        type=str,
        help="目标Git仓库目录路径"
    )
    args = parser.parse_args()
    
    try:
        process_repository(args.directory)
        logger.info("操作成功完成")
    except GitSyncError:
        logger.error("程序因错误退出")
        exit(1)
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        exit(130)
    except Exception as e:
        logger.error(f"未处理的异常: {str(e)}")
        exit(2)

if __name__ == "__main__":
    main()
