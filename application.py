from sys import exit
# from decouple import config
from apps.config import config_dict
from apps import create_app

get_config_mode = 'Production'

try:
    app_config = config_dict[get_config_mode]
except KeyError:
    exit('Error: Invalid <config_mode>')

application = create_app(app_config)
app = application

app.jinja_env.globals.update(len=len)
app.jinja_env.globals.update(enumerate=enumerate)

if __name__ == '__main__':
    app.run()