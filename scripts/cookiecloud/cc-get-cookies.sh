#!/usr/bin/env bash
set -euo pipefail

VERSION="1.0.0"

usage() {
  cat <<EOF
CookieCloud Cookie 导出工具 v${VERSION}

Usage: $(basename "$0") -s SERVER -u UUID -p PASSWORD [-d DOMAIN]

Options:
  -s SERVER    CookieCloud 服务器地址
  -u UUID      用户 UUID
  -p PASSWORD  端对端加密密码
  -d DOMAIN    筛选域名 (关键字匹配, 留空输出全部)
  -h           显示帮助
  -v           显示版本号

示例:
  # 获取指定域名 cookie (直接用于 curl -b)
  $(basename "$0") -s https://your-server.com -u <UUID> -p <PASSWORD> -d example.com

  # 获取全部 cookie (按域名分组输出)
  $(basename "$0") -s https://your-server.com -u <UUID> -p <PASSWORD>

  # 配合 curl 使用
  curl -b "\$($(basename "$0") -s https://your-server.com -u <UUID> -p <PASSWORD> -d example.com)" https://example.com/
EOF
}

die() { echo "错误: $*" >&2; exit 1; }

SERVER="" UUID="" PASS="" DOMAIN=""

while getopts "s:u:p:d:hv" opt; do
  case $opt in
    s) SERVER="$OPTARG" ;;
    u) UUID="$OPTARG" ;;
    p) PASS="$OPTARG" ;;
    d) DOMAIN="$OPTARG" ;;
    h) usage; exit 0 ;;
    v) echo "v${VERSION}"; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

[[ -z "$SERVER" ]] && die "缺少服务器地址 (-s)"
[[ -z "$UUID" ]]   && die "缺少 UUID (-u)"
[[ -z "$PASS" ]]   && die "缺少加密密码 (-p)"
command -v jq >/dev/null || die "需要 jq (brew install jq)"

# POST password 让服务端解密，保存到临时文件
body=$(mktemp)
trap 'rm -f "$body"' EXIT
http_code=$(curl -sf --max-time 15 --connect-timeout 5 --retry 2 --retry-delay 1 \
  -o "$body" -w "%{http_code}" -X POST "${SERVER%/}/get/${UUID}" \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"${PASS}\"}") || die "请求服务器失败: ${SERVER}"

[[ "$http_code" == "404" ]] && die "UUID 不存在"
[[ "$http_code" != "200" ]] && die "服务器返回 HTTP ${http_code}"

if [[ -n "$DOMAIN" ]]; then
  # 指定域名: 输出 "name=value; name2=value2" 格式，可直接用于 curl -b
  result=$(jq -r --arg d "$DOMAIN" '
    [.cookie_data | to_entries[] | select(.key | contains($d)) | .value[]]
    | map("\(.name)=\(.value)") | join("; ")
  ' "$body")
  [[ -z "$result" ]] && die "未找到匹配域名「${DOMAIN}」的 cookie"
  echo "$result"
else
  # 未指定域名: 按域名分组输出
  jq -r '
    [.cookie_data | to_entries[] | {
      domain: .key,
      cookies: [.value[] | "\(.name)=\(.value)"] | join("; ")
    }]
    | .[] | "\(.domain)\t\(.cookies)"
  ' "$body"
fi

