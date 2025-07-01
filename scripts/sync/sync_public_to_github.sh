#!/bin/bash

# 检查参数
if [ $# -ne 1 ]; then
    echo "错误：请提供一个目录路径作为参数"
    exit 1
fi

hugo_dir="${1%/}"
public_dir="${hugo_dir}/public"
target_dir="${hugo_dir%/*}/linlishui.github.io"  # 获取hugo_dir的父目录

# 验证public目录是否存在
if [ ! -d "$public_dir" ]; then
    echo "错误：未找到public目录 - $public_dir"
    exit 1
fi

# 检查目标目录是否存在，不存在则尝试克隆
if [ ! -d "$target_dir" ]; then
    echo "目标目录不存在，尝试从GitHub克隆..."
    parent_dir="$(dirname "$hugo_dir")"
    cd "$parent_dir" || exit 1
    git clone git@github.com:linlishui/linlishui.github.io.git
    
    # 再次验证是否克隆成功
    if [ ! -d "$target_dir" ]; then
        echo "错误：克隆后目标目录仍不存在 - $target_dir"
        exit 1
    fi
fi

# 同步public目录内容到目标目录（排除.git目录和.gitignore文件）
echo "正在同步内容到: $target_dir"
rsync -a --delete --exclude='.git' --exclude='.gitignore' "$public_dir/" "$target_dir" || {
    echo "错误：同步失败"
    exit 1
}

# 在目标目录执行git操作
cd "$target_dir" || exit 1

# 获取当前分支名称
current_branch=$(git rev-parse --abbrev-ref HEAD)

# 检查是否有变更
if [ -n "$(git status --porcelain)" ]; then
    echo "检测到变更，正在提交..."
    git add . && \
    git commit -m "note: sync blog from server" && \
    git push origin "$current_branch"
    
    # 检查推送是否成功
    if [ $? -eq 0 ]; then
        echo "✅ 同步完成并成功推送到GitHub分支: $current_branch"
    else
        echo "❌ 推送失败，请检查Git配置和权限"
        exit 1
    fi
else
    echo "无变更可提交"
fi