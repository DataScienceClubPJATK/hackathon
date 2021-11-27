##
import pandas as pd
import geopandas as gpd
import googlemaps
import unidecode
import re
import folium
import matplotlib.pyplot as plt
##

def get_prenormalised(df: pd.DataFrame):
    df['prenormalised'] = df.apply(
        lambda row: f'{row["Street"]} {row["StreetNumber"]}, {row["PostalCode"]} {row["City"]}', axis=1)
    df['prenormalised'] = df['prenormalised'].apply(unidecode.unidecode)
    return df


def reshape_geocode(geocode):
    geocode_dict = {}
    for obj in geocode[0]['address_components']:
        if obj.get('types'):
            geocode_dict[obj['types'][0]] = obj['long_name']
    geocode_dict['formatted_address'] = geocode[0]['formatted_address']
    geocode_dict['lat'] = geocode[0]['geometry']['location']['lat']
    geocode_dict['lng'] = geocode[0]['geometry']['location']['lng']
    geocode_dict['place_id'] = geocode[0]['place_id']
    return geocode_dict


def get_api_data(gmaps_obj, df):
    df['geocode'] = df.apply(lambda row: reshape_geocode(gmaps_obj.geocode(row['prenormalised'])), axis=1)
    return df


def postal_code_validator(row):
    from_api = row['geocode']['formatted_address']
    if re.match(r'[0-9][0-9]\-[0-9][0-9][0-9]', from_api):
        return from_api
    else:
        return row['PostalCode']


def get_geocodes(df):
    df['street_number_n'] = df.apply(lambda row: row['geocode']['street_number'], axis=1)
    df['route_n'] = df.apply(lambda row: row['geocode']['route'], axis=1)
    df['locality_n'] = df.apply(lambda row: row['geocode']['locality'], axis=1)
    df['administrative_area_level_2_n'] = df.apply(lambda row: row['geocode']['administrative_area_level_2'], axis=1)
    df['postal_code_n'] = df.apply(postal_code_validator, axis=1)
    df['formatted_address_n'] = df.apply(lambda row: row['geocode']['formatted_address'], axis=1)
    df['lat_n'] = df.apply(lambda row: row['geocode']['lat'], axis=1)
    df['lng_n'] = df.apply(lambda row: row['geocode']['lng'], axis=1)
    df['place_id_n'] = df.apply(lambda row: row['geocode']['place_id'], axis=1)
    return df


def get_df_with_geocodes(locations_path: str, start_path: str):
    gmaps = googlemaps.Client(key='AIzaSyC9TxvgLQ-laKATF0wZBxTZw3uYOMfF1oM')
    df = pd.read_json(locations_path)
    df['isStart'] = False
    _df = pd.read_json(start_path, typ='series')
    _df['isStart'] = True
    df = df.append(_df, ignore_index=True)
    df = get_prenormalised(df)
    df = get_api_data(gmaps, df)
    df = get_geocodes(df)
    return df


def get_data_time_matrix(df):
    gmaps = googlemaps.Client(key='AIzaSyC9TxvgLQ-laKATF0wZBxTZw3uYOMfF1oM')
    places=df.loc[5:10].formatted_address_n.tolist()
    return gmaps.distance_matrix(places,places)



##
locations_path = r"/Users/damian/PycharmProjects/hackathon/locations.json"
start_path = r"/Users/damian/PycharmProjects/hackathon/startPoint.json"

df = get_df_with_geocodes(locations_path, start_path)

##
matrix = get_data_time_matrix(df)

##
df_matrix = pd.DataFrame(matrix)

##
