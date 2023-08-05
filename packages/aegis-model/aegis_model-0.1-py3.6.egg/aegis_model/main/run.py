from wows_stats.model.winrate_model import build_winrate_model

from aegis_data.api.wows_api import WowsAPIRequest

START_DATE = '2019-09-18'
CONFIG_FILE = ""


def database_update():
    WowsAPIRequest(CONFIG_FILE).request_historical_stats_all_accounts_last_month(start_date=START_DATE)


def model_update():
    build_winrate_model()


if __name__ == '__main__':
    database_update()
    model_update()
    print("Main function finished!")
