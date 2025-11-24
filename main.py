# main.py
from api.server import MeterAPI
from settings import Settings
from lib.gen_ai import GenAI

if __name__ == "__main__":

    settings = Settings()

    gen_ai = GenAI(settings)
    server = MeterAPI(gen_ai, settings)

    server.run(host=settings.config.get('host'),
               port=settings.config.get('port'))
