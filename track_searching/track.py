##
import pandas as pd

from data_processing.google_api import get_df_with_geocodes, get_data_time_matrix
##

class TrackFinder:
    def __init__(self, start_point_path, points_path, seconds_spent_on_point):
        self.environment = Environment(start_point_path, points_path, seconds_spent_on_point)
        start_point_idx = self.environment.points[self.environment.points['isStart']].index.values[0]
        self.vehicle = Vehicle(start_point_idx)
        self.df_results = None
    def move_vehicle(self):
        # quered_time_matrix = self.environment.query_point_time(self.vehicle.actual_point)
        quered_time_matrix = self.environment.query_dynamic_point_time(self.vehicle.actual_point)
        choosen_point = self.vehicle.choose_point(quered_time_matrix)
        distance = self.environment.visit_point(self.vehicle.actual_point, choosen_point)
        self.vehicle.actual_point = choosen_point
        self.vehicle.distance_driven += distance
        history_log = {'point_id':choosen_point,'time_spent': self.environment.virtual_time, 'distance_driven': self.vehicle.distance_driven}
        self.vehicle.track_history = self.vehicle.track_history.append(history_log, ignore_index=True)

    def find_track(self):
        for i in range(0, len(self.environment.points) -1):
            self.move_vehicle()
        self.df_results = pd.merge(self.vehicle.track_history, self.environment.points, left_on='point_id', right_index=True)
        return self.df_results

class Vehicle:
    def __init__(self,start_point):
        self.actual_point = start_point
        self.distance_driven = 0
        self.track_history = pd.DataFrame(columns=['point_id', 'time_spent', 'distance_driven']) #point_id, virutal time timestamp (work done)

    def choose_point(self, quered_time_matrix, sortby = 'duration'):
        assert sortby in ['duration', 'distance']
        if sortby == 'duration':
            sorted = quered_time_matrix.sort_values(by='duration')
        elif sortby == 'distance':
            sorted = quered_time_matrix.sort_values(by='distance')
        return sorted.head(1).index.values[0]

class Environment:
    def __init__(self, start_point_path, points_path, seconds_spent_on_point):
        self.seconds_spent_on_point = seconds_spent_on_point
        self.points = get_df_with_geocodes(start_point_path, points_path)
        self.points['visited'] = False
        self.virtual_time = self.query_min_time()
        current_point = self.points[self.points['isStart']].index.values[0]
        self.time_matrix = get_data_time_matrix(self.points, arr_time=self.virtual_time, current_point=current_point)

    def query_min_time(self):
        return self.points['OpenTime'].min()

    def query_open_points_indexes(self):
        points = self.points[self.points['visited'] != True]
        return points[(points['OpenTime'] <= self.virtual_time) & (points['CloseTime'] >= self.virtual_time)].index.tolist()

    def query_point_time(self, actual_point):
        quered = self.query_open_points_indexes()
        quered = [x for x in quered if x != actual_point]
        open_points_time_matrix = self.time_matrix.loc[actual_point].loc[quered]
        return open_points_time_matrix

    def query_dynamic_point_time(self, actual_point):
        quered = self.query_open_points_indexes()
        quered = [x for x in quered if x != actual_point]
        time_matrix = get_data_time_matrix(self.points, arr_time=self.virtual_time, current_point=actual_point)
        open_points_time_matrix = time_matrix.loc[actual_point].loc[quered]
        return open_points_time_matrix

    add_seconds_to_vtime = lambda self, t: self.virtual_time + pd.Timedelta(t, unit='s')
    remove_seconds_from_vtime = lambda self, t: self.virtual_time - pd.Timedelta(t, unit='s')

    def visit_point(self, start_point_idx, end_point_idx):
        distance_matrix_row = get_data_time_matrix(self.points, arr_time=self.virtual_time, current_point=start_point_idx).loc[start_point_idx, end_point_idx]
        self.points.at[start_point_idx, 'visited'] = True #t0
        # wyruszamy przed czasem otwarcia pierwszego punktu
        if self.virtual_time == self.query_min_time():
            self.virtual_time = self.remove_seconds_from_vtime(distance_matrix_row['duration'])
        self.virtual_time = self.add_seconds_to_vtime(distance_matrix_row['duration']) # #t0 -> t1
        self.virtual_time = self.add_seconds_to_vtime(self.seconds_spent_on_point) #self.seconds_spent_on_point #t1 -> t2
        self.points.at[end_point_idx, 'visited'] = True
        return distance_matrix_row['distance']

# ##
# a = r"/Users/damian/PycharmProjects/hackathon/startPoint.json"
# b = r"/Users/damian/PycharmProjects/hackathon/locations.json"
# #
# tr = TrackFinder(a,b, 240)
# res = tr.find_track()
# #
# #

##

