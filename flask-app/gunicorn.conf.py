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
def on_starting(server):
    """Gunicornワーカープロセス起動時に呼ばれる"""
    print("Gunicorn master process starting...")

def when_ready(server):
    """Gunicornワーカープロセス準備完了時に呼ばれる"""
    print("Gunicorn workers are ready")

def worker_int(worker):
    """ワーカープロセス終了時に呼ばれる"""
    print(f"Worker {worker.pid} is shutting down")

def pre_fork(server, worker):
    """ワーカープロセス起動前に呼ばれる"""
    print(f"About to fork worker {worker.age}")

def post_fork(server, worker):
    """ワーカープロセス起動後に呼ばれる"""
    print(f"Worker {worker.pid} started")
    # ワーカープロセス内でワーカースレッドを起動
    from app import start_worker
    start_worker()
    print(f"Worker {worker.pid} worker thread started")

def worker_exit(server, worker):
    """ワーカープロセス終了時に呼ばれる"""
    print(f"Worker {worker.pid} is exiting")
    # 進行中のジョブがあれば、キューに戻す処理をここで行う
    # ただし、現在の実装では進行中のジョブは完了まで待機
