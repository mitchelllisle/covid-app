from pydantic import BaseSettings, Field
from datetime import date
import pandas as pd


def get_data() -> pd.DataFrame:
    return pd.read_csv(
            'https://raw.githubusercontent.com/M3IT/COVID-19_Data/master/Data/COVID_AU_state.csv'
        )


class AssetConfig(BaseSettings):
    logo = '/assets/logo.jpg'


class DataConfig(BaseSettings):
    min_date: date = date(2020, 1, 25)
    data: pd.DataFrame = Field(
        default_factory=get_data
    )


class ColourConfig(BaseSettings):
    light_gray: str = '#ECECF1'
    dark_gray: str = '#47474'
    blue: str = '#445DED'
    green: str = '#7ED321'
    red: str = '#F5718F'
    pink: str = '#D67FD2'
    orange: str = '#FDB39F'
    aqua: str = '#64CFB7'


class Config(BaseSettings):
    assets: AssetConfig = AssetConfig()
    colours: ColourConfig = ColourConfig()
    data: DataConfig = DataConfig()
