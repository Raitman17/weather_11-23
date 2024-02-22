HOST, PORT = '127.0.0.1', 8000

OK = 200
NO_CONTENT = 204
BAD_REQUEST = 400
FORBIDDEN = 403
SERVER_ERROR = 500
NOT_FOUND = 404
NOT_ALLOWED = 405

CONTENT_TYPE = 'html'  # NOTE switch content
CONTENT_HEADER = 'Content-Type', f'text/{CONTENT_TYPE}'
ALLOW_HEADER = {'Allow': '[GET, HEAD]'}

TEMPLATES = 'templates/'
TEMPLATE_MAIN = f'{TEMPLATES}index.html'
TEMPLATE_WEATHER = f'{TEMPLATES}weather.html'
TEMPLATE_WEATHER_DUMMY = f'{TEMPLATES}weather_dummy.html'
TEMPLATE_CITIES = f'{TEMPLATES}cities.html'

YANDEX_HEADER = 'X-Yandex-API-Key'
YANDEX_URL = 'https://api.weather.yandex.ru/v2/informers'
WEATHER_KEYS = 'temp', 'feels_like', 'wind_speed'

TIMEOUT = 8
