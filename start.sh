#!/bin/bash
# StudyAgent 启动脚本（DeepSeek 模式）
cd "$(dirname "$0")"
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
echo "🚀 StudyAgent 启动中 (LLM: $LLM_MODE)..."
streamlit run frontend/app.py
