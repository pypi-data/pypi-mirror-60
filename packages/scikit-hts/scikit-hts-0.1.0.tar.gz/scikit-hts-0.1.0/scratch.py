import numpy as np
import pandas as pd

from hts.foreacast import HierarchicalProphet as HP

date = pd.date_range('2015-04-02', '2017-07-17')
date = np.repeat(date, 10)

country = ['Germany']
cities = ['Berlin', 'Hamburg']
district = ['Mitte', 'Kreuzberg', 'Fredechsein', 'Hamburg-Mitte', 'Altona']

district_rides = np.random.randint(1000, 10000, size=(len(date), len(district)))
b_city_rides = district_rides[:, :3].sum(axis=1)
h_city_rides = district_rides[:, 3:].sum(axis=1)
country_rides = district_rides.sum(axis=1)


data = {
    'time': date,
    'Total': country_rides,
    'Germany_Berlin': b_city_rides,
    'Germany_Hamburg': h_city_rides,
    'Germany_Berlin_Mitte': district_rides[:, 0],
    'Germany_Berlin_Kreuzberg': district_rides[:, 1],
    'Germany_Berlin_Fredechsein': district_rides[:, 2],
    'Germany_Hamburg_Hamburg-Mitte': district_rides[:, 3],
    'Germany_Hamburg_Altona': district_rides[:, 4],

}

df = pd.DataFrame(data)

holidates = pd.date_range('12/25/2013', '12/31/2017', freq='A')
holidays = pd.DataFrame(['Christmas'] * 5, columns=['holiday'])
holidays['ds'] = holidates
holidays['lower_window'] = [-4] * 5
holidays['upper_window'] = [0] * 5

nodes = [[2], [3, 2]]

if __name__ == '__main__':
    m = HP(periods=52, nodes=nodes, holidays=holidays, method='FP', transform=True)
    m.fit(df)
