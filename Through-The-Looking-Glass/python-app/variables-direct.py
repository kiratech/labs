APP_DEBUG=False
APP_FRONTEND_NAME='alice'
APP_FRONTEND_HOST='172.18.0.1'
APP_FRONTEND_PORT=5000
APP_BACKEND_NAME='cheshire'
APP_BACKEND_HOST='172.18.0.1'
APP_BACKEND_PORT=5001
APP_BACKEND_URL=f"http://{APP_BACKEND_HOST}:{APP_BACKEND_PORT}/process"
TRACES_ENDPOINT='172.18.0.103:4317'                       # Tempo exposed IP
LOGS_ENDPOINT='http://172.18.0.104:8080/loki/api/v1/push' # Loki exposed IP
