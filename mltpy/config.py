from __future__ import annotations

import os

# クラウドレンダラーのベースURL（例: http://163.58.36.32）
# 環境変数 CLOUD_RENDER_BASE_URL があればそれを優先
CLOUD_RENDER_BASE_URL: str = os.getenv("CLOUD_RENDER_BASE_URL", "http://163.58.36.32:5000").rstrip("/")


