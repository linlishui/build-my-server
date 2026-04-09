#!/bin/bash

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

usage() {
    echo "Usage:"
    echo "$0 [-m msg] [-M]"
    echo "Description:"
    echo "[-m msg] -> the message for git to commit."
    echo "[-M]      -> merge mode: add, commit --no-edit, push (for post-merge upload)."
    exit 1
}

git_commit_msg=""
merge_mode=false

while getopts "m:Mh" opt;
do
    case $opt in
        m)
        git_commit_msg=$OPTARG
        ;;
        M)
        merge_mode=true
        ;;
        h)
        usage
        ;;
        ?)
        echo -e "${RED}无效选项: -$OPTARG${NC}"
        usage
        ;;
    esac
done


function projectGitState() {
	gbranch=$(git branch --show-current)
	gcount=$(git rev-list --count HEAD)
	echo "代码分支：$gbranch"
	echo "代码版本：$gcount"
}


function checkMergeConflicts() {
	conflict_files=$(git diff --name-only --diff-filter=U 2>/dev/null)
	if [ -n "$conflict_files" ]; then
		echo -e "${RED}----- 检测到合并冲突！-----${NC}"
		echo -e "${YELLOW}冲突文件列表：${NC}"
		echo "$conflict_files" | while read -r file; do
			echo -e "  ${RED}✗${NC} $file"
		done
		echo ""
		echo -e "${YELLOW}请手动解决冲突后再运行此脚本！${NC}"
		echo -e "提示：使用 ${GREEN}git diff --name-only --diff-filter=U${NC} 查看冲突文件"
		echo -e "      使用 ${GREEN}git diff${NC} 查看冲突详情"
		exit 1
	fi
}


function mergeAndPush() {
	checkMergeConflicts

	echo -e "${GREEN}----- [合并模式] 开始执行 git add -----${NC}"
	add_output=$(git add -A 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git add 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}${add_output}"
		exit 1
	fi

	echo -e "${GREEN}----- [合并模式] 开始执行 git commit --no-edit -----${NC}"
	commit_output=$(git commit --no-edit 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git commit --no-edit 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}"
		echo "${commit_output}"
		exit 1
	fi
	echo "${commit_output}"

	echo -e "${GREEN}----- [合并模式] 开始执行 git push -----${NC}"
	push_output=$(git push 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git push 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}"
		echo "${push_output}"
		exit 1
	fi
	echo "${push_output}"

	echo -e "${GREEN}----- [合并模式] 已成功推送代码到远程仓库！-----${NC}"
}


function commitToPush() {
	if [ -z "$git_commit_msg" ]; then
		echo -e "${RED}----- 缺少提交（commit）的信息！-----${NC}"
		exit 1
	fi

	checkMergeConflicts

	oldCommitNotPush=$(git cherry -v 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git cherry 执行失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}${oldCommitNotPush}"
		exit 1
	fi
	if [ "$oldCommitNotPush" ]; then
		echo "存在以下提交项未推送："
		echo "${oldCommitNotPush}"
		echo -e "${RED}----- 请手动执行 git push 操作后再运行此脚本！-----${NC}"
		exit 1
	fi

	echo -e "${GREEN}----- 开始执行 git add -----${NC}"
	add_output=$(git add -A 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git add 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}${add_output}"
		exit 1
	fi

	echo -e "${GREEN}----- 开始执行 git commit -----${NC}"
	commit_output=$(git commit -m "${git_commit_msg}" 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git commit 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}"
		echo "${commit_output}"
		exit 1
	fi
	echo "${commit_output}"

	echo -e "${GREEN}----- 开始执行 git push -----${NC}"
	push_output=$(git push 2>&1)
	if [ $? -ne 0 ]; then
		echo -e "${RED}----- git push 失败 -----${NC}"
		echo -e "${YELLOW}错误信息：${NC}"
		echo "${push_output}"
		exit 1
	fi
	echo "${push_output}"

	echo -e "${GREEN}----- 已成功推送代码到远程仓库！-----${NC}"
}

if [ "$merge_mode" = true ]; then
	mergeAndPush
else
	commitToPush
fi

projectGitState