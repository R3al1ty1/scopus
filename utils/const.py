import os


REQUESTS_DCT = {
    49: 1,
    229: 5,
    419: 10,
    799: 20,
    999: 300,
    1499: 500,
    1999: 800,
}

AMOUNTS_DCT = {
    'button_1': 49,
    'button_5': 229,
    'button_10': 419,
    'button_20': 799,
    'small': 999,
    'medium': 1499,
    'large': 1999,
}

DESCRIPTIONS_DCT = {
    49: "Покупка 1 запроса",
    229: "Покупка 5 запросов",
    419: "Покупка 10 запросов",
    799: "Покупка 20 запросов",
    999: "Покупка 300 запросов",
    1499: "Покупка 500 запросов",
    1999: "Покупка 800 запросов",
}

project_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR= os.path.dirname(project_dir)
