import pandas as pd


class GTFS:
    def __init__(self, routes_path, stops_path, stop_times_path, trips_path):
        self.start_trips = None
        self.end_trips = None

        self.stops_df = pd.read_csv(stops_path, sep=',')
        self.stops_df['stop_name_id'] = self.stops_df['stop_name'] + ' ' + self.stops_df['stop_id'].map(str)

        self.routes_df = pd.read_csv(routes_path, sep=',')
        self.trips_df = pd.read_csv(trips_path, sep=',')
        self.stop_times_df = pd.read_csv(stop_times_path, sep=',')

        self.stop_names_id = self.stops_df['stop_name_id']
        self.stop_names_id = self.stop_names_id.sort_values()

        self.stops_trip_df = self.stop_times_df[['trip_id', 'stop_id']]
        self.start_onehop_stops = None
        self.end_onehop_stops = None
        self.onehop_set = None
        self.zerohop_set = None

    def zero_hop(self, start_stop_id, end_stop_id):
        self.start_trips = self.stops_trip_df[self.stops_trip_df.stop_id == start_stop_id][['trip_id']]
        self.end_trips = self.stops_trip_df[self.stops_trip_df.stop_id == end_stop_id][['trip_id']]
        self.zerohop_set = set(self.start_trips['trip_id']).intersection(set(self.end_trips['trip_id']))
        return len(self.zerohop_set) > 0

    def one_hop(self, start_stop_id, end_stop_id):
        self.start_trips = self.stops_trip_df[self.stops_trip_df.stop_id == start_stop_id][['trip_id']]
        self.end_trips = self.stops_trip_df[self.stops_trip_df.stop_id == end_stop_id][['trip_id']]
        self.start_onehop_stops = self.stops_trip_df[self.stops_trip_df.trip_id.isin(self.start_trips['trip_id'])][
            'stop_id']
        self.end_onehop_stops = self.stops_trip_df[self.stops_trip_df.trip_id.isin(self.end_trips['trip_id'])][
            'stop_id']
        self.onehop_set = set(self.start_onehop_stops).intersection(set(self.end_onehop_stops))
        return len(self.onehop_set) > 0

    def get_stop_from_stop_name_id(self, stop_name_id):
        frame = self.stops_df[self.stops_df.stop_name_id == stop_name_id]
        stop = frame.to_dict(orient='records')
        return stop[0]

    def zerohop_trips(self):
        return self.zerohop_set

    def onehop_trips(self):
        first_trip = self.stop_times_df[
            self.stop_times_df.trip_id.isin(self.start_trips['trip_id']) & self.stop_times_df.stop_id.isin(
                self.onehop_set)]
        second_trip = self.stop_times_df[
            self.stop_times_df.trip_id.isin(self.end_trips['trip_id']) & self.stop_times_df.stop_id.isin(
                self.onehop_set)]

        first_trip = first_trip.drop(columns=['stop_sequence'])
        second_trip = second_trip.drop(columns=['stop_sequence'])

        first_trip.columns = ['first_trip_id', 'first_tp_arrival_time', 'first_tp_departure_time', 'stop_id']
        second_trip.columns = ['second_trip_id', 'second_tp_arrival_time', 'second_tp_departure_time', 'stop_id']

        result = pd.merge(first_trip, second_trip, how='inner', on='stop_id', left_index=False, right_index=False,
                          sort=True).drop(columns=['stop_id'], axis=1).to_dict(orient='records')

        return result
