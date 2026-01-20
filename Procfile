web: gunicorn web_dashboard:app --bind 0.0.0.0:$PORT
worker: python copy_trade_worker.py --mainnet
