APP_FRONTEND_NAME='alice'
APP_FRONTEND_PORT=5000
APP_BACKEND_NAME='cheshire'
APP_BACKEND_PORT=5001
APP_BACKEND_URL=f"http://localhost:{APP_BACKEND_PORT}/process"
TRACES_OTLP_ENDPOINT='172.18.0.103:4317'
LOGS_URL='http://172.18.0.104:8080/loki/api/v1/push'
