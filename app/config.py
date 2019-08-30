class Config:
    SECRET_KEY = '3b4c830cd7d88c05cfa5d6da59af4561'


class Development(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@127.0.0.1:5432/invoice_generator'
    DEBUG = True


class Production(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = ''

    DEBUG = False