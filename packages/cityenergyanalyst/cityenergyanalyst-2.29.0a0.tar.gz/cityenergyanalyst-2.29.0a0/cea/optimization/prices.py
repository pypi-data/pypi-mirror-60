# -*- coding: utf-8 -*-
"""
This file imports the price details from the cost database as a class. This helps in preventing multiple importing
of the corresponding values in individual files.
"""
from __future__ import division
import pandas as pd
import numpy as np
from cea.constants import HOURS_IN_YEAR

__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2019, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"


class Prices(object):
    def __init__(self, supply_systems, detailed_electricity_pricing):
        pricing = supply_systems.FEEDSTOCKS
        self.NG_PRICE = pricing[pricing['code'] == 'NATURALGAS'].iloc[0]['Opex_var_buy_USD2015perkWh'] / 1000 # in USD/Wh
        self.BG_PRICE = pricing[pricing['code'] == 'BIOGAS'].iloc[0]['Opex_var_buy_USD2015perkWh']  / 1000# in USD/Wh
        self.WB_PRICE = pricing[pricing['code'] == 'WETBIOMASS'].iloc[0]['Opex_var_buy_USD2015perkWh']  / 1000# in USD/Wh
        self.DB_PRICE = pricing[pricing['code'] == 'DRYBIOMASS'].iloc[0]['Opex_var_buy_USD2015perkWh'] / 1000 # in USD/Wh
        self.SOLAR_PRICE = pricing[pricing['code'] == 'SOLAR'].iloc[0]['Opex_var_buy_USD2015perkWh']  / 1000# in USD/Wh
        self.SOLAR_PRICE_EXPORT = pricing[pricing['code'] == 'SOLAR'].iloc[0]['Opex_var_sell_USD2015perkWh'] / 1000 # in USD/Wh

        if detailed_electricity_pricing:
            electricity_costs = supply_systems.DETAILED_ELEC_COSTS
            self.ELEC_PRICE = electricity_costs['Opex_var_buy_USD2015perkWh'].values / 1000  # in USD_2015 per Wh
            self.ELEC_PRICE_EXPORT = electricity_costs['Opex_var_sell_USD2015perkWh'].values / 1000  # in USD_2015 per Wh
        else:
            average_electricity_price = pricing[pricing['code'] == 'GRID'].iloc[0]['Opex_var_buy_USD2015perkWh'] / 1000
            average_electricity_selling_price = pricing[pricing['code'] == 'GRID'].iloc[0]['Opex_var_sell_USD2015perkWh'] / 1000
            self.ELEC_PRICE = np.ones(HOURS_IN_YEAR) * average_electricity_price  # in USD_2015 per Wh
            self.ELEC_PRICE_EXPORT = np.ones(HOURS_IN_YEAR) * average_electricity_selling_price  # in USD_2015 per Wh

