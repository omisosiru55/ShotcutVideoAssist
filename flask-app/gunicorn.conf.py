# Gunicorn設定ファイル

# サーバー設定
bind = "0.0.0.0:5000"
workers = 1
threads = 4
worker_class = "gthread"

# メモリ管理
max_requests_jitter = 0

# ログ設定
accesslog = "-"
errorlog = "-"
loglevel = "info"

# プロセス設定
max_requests = 10000  # 無制限（0で無効化）
timeout = 300
keepalive = 2

# ワーカープロセス設定
preload_app = False
reload = False

# Gunicornフック関数
def post_fork(server, worker):
    """ワーカープロセス起動後に呼ばれる"""
    print(f"Worker {worker.pid} started")
    # ワーカープロセス内でワーカースレッドを起動
    from app import start_worker
    start_worker()
    print(f"Worker {worker.pid} worker thread started")
