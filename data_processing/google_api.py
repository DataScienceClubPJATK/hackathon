##
import pandas as pd
import googlemaps
import unidecode
import re
from tqdm import tqdm
from more_itertools import sliced
import datetime
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
    df['OpenTime'] = df.apply(lambda row: datetime.datetime.fromisoformat(f"{datetime.date.today()} {row['OpenTime']}") if not row['isStart']  else None, axis=1)
    df['CloseTime'] = df.apply(lambda row: datetime.datetime.fromisoformat(f"{datetime.date.today()} {row['CloseTime']}") if not row['isStart'] else None, axis=1)
    return df


def get_df_with_geocodes(start_path: str, locations_path: str):
    gmaps = googlemaps.Client(key='AIzaSyC9TxvgLQ-laKATF0wZBxTZw3uYOMfF1oM')
    df = pd.read_json(locations_path)
    df['isStart'] = False
    _df = pd.read_json(start_path, typ='series')
    _df['isStart'] = True
    df = df.append(_df, ignore_index=True)
    df = get_prenormalised(df)
    df = get_api_data(gmaps, df)
    df = get_geocodes(df)
    df.drop_duplicates(subset='formatted_address_n', keep='last', inplace=True)
    return df

def reshape_distance_response(resp):
    return [{'distance': res['distance']['value'], 'duration': res['duration']['value']} for res in resp['rows'][0]['elements']]


def get_data_time_matrix(df, limit=25):
    gmaps = googlemaps.Client(key='AIzaSyC9TxvgLQ-laKATF0wZBxTZw3uYOMfF1oM')
    places = df[['formatted_address_n','OpenTime', 'CloseTime', 'index']]
    df_matrix = pd.DataFrame()
    for _, place_A in tqdm(places.iterrows()):
        for places_B in sliced(places, limit):
            matrix = gmaps.distance_matrix(place_A['formatted_address_n'], places_B['formatted_address_n'], mode='driving')
            for i, res in enumerate(reshape_distance_response(matrix)):
                ret_dict = {"from_idx": place_A['index'], "to_idx": places_B.iloc[i]['index'], "from": place_A['formatted_address_n'],
                            "to": places_B.iloc[i]['formatted_address_n'], "distance": res['distance'],
                            "duration": res['duration'], "dest_closeTime": places_B.iloc[i]['CloseTime']}
                df_matrix = df_matrix.append(ret_dict, ignore_index=True)
    df_matrix = df_matrix.astype({"from_idx": int, "to_idx": int})
    df_matrix = df_matrix[df_matrix['from_idx'] != df_matrix['to_idx']]
    df_matrix.set_index(['from_idx', 'to_idx'], inplace=True)
    return df_matrix



