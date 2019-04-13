import pandas as pd


class GTFS:

    # CLASS having stops, routes, trips, stop_times as dataframes
    # methods perform finding routes from one stop to other

    def __init__(self, routes_path, stops_path, stop_times_path, trips_path):
        # READ all gtfs files and store in dataframes
        self.stops_df = pd.read_csv(stops_path, sep=',')
        self.stops_df['stop_name_id'] = self.stops_df['stop_name'] + ' ' + self.stops_df['stop_id'].map(str)

        self.routes_df = pd.read_csv(routes_path, sep=',')
        self.trips_df = pd.read_csv(trips_path, sep=',')
        self.stop_times_df = pd.read_csv(stop_times_path, sep=',')

        # CREATE Series containing the names_id combination from stops file, for user input
        self.stop_names_id = self.stops_df['stop_name_id']
        self.stop_names_id = self.stop_names_id.sort_values()

        # CREATE helper dataframe to optimize the performance and removing redundant fields.
        self.stops_trip_df = self.stop_times_df[['trip_id', 'stop_id']]

        # Following variables will be filled by methods and will be passed as input to the application
        self.start_trips = None
        self.end_trips = None
        self.start_onehop_stops = None
        self.end_onehop_stops = None
        self.onehop_set = None
        self.zerohop_set = None

    def zero_hop(self, start_stop_id, end_stop_id):
        """
           :param: start_stop_id, end_stop_id
           Description:
                    start_stop_id-> integer id of the start stop
                    end_stop_od -> integer id of the end stop

            Procedure:
            find all trips having start stop in their route, also find all trips having end stop in their route
            filter only those trips which have both these stops in common.

            During procedure, store all the zero hop trips in memory for later use

            :returns true/false (if common trips exist then true, else false)
        """
        self.start_trips = self.stops_trip_df[self.stops_trip_df.stop_id == start_stop_id][['trip_id']]
        self.end_trips = self.stops_trip_df[self.stops_trip_df.stop_id == end_stop_id][['trip_id']]
        self.zerohop_set = set(self.start_trips['trip_id']).intersection(set(self.end_trips['trip_id']))
        return len(self.zerohop_set) > 0

    def one_hop(self, start_stop_id, end_stop_id):
        """
            :param : start_stop_id, end_stop_id

            Procedure:
            find all trips having start stop in their route, also find all trips having end stop in their route
            find all the stops that can be reached from start stop in one hop.
            do the same for end stop
            then filter only the common stops in these stops.
            filtered stops are intersection points, store for future use.

            :returns true/false (if one hop paths found, true else false)

        """
        self.start_trips = self.stops_trip_df[self.stops_trip_df.stop_id == start_stop_id][['trip_id']]
        self.end_trips = self.stops_trip_df[self.stops_trip_df.stop_id == end_stop_id][['trip_id']]
        self.start_onehop_stops = self.stops_trip_df[self.stops_trip_df.trip_id.isin(self.start_trips['trip_id'])][
            'stop_id']
        self.end_onehop_stops = self.stops_trip_df[self.stops_trip_df.trip_id.isin(self.end_trips['trip_id'])][
            'stop_id']
        self.onehop_set = set(self.start_onehop_stops).intersection(set(self.end_onehop_stops))
        return len(self.onehop_set) > 0


    def get_stop_from_stop_name_id(self, stop_name_id):
        """
            Method to get stop given its name_id combination
            :param : stop_name_id

            Procedure: search in stops dataframe

            :returns dict(stop) || None (not found)
        """
        frame = self.stops_df[self.stops_df.stop_name_id == stop_name_id]
        stop = frame.to_dict(orient='records')
        if stop is not None:
            return stop[0]
        else:
            return None

    def zerohop_trips(self):
        """  Returns the set of common stops obtained in zero_hop method"""
        return self.zerohop_set

    def onehop_trips(self):
        """
            Method to get trips starting from given start stop
            another trip interchanging at some intermediate stop to reach end stop
            :param : stop_name_id

            Procedure:
            Use the onehop_set obtained in one_hop(,) method and find the trips
            from start stop having stops in onehop_set (intermediate stops).
            Same for end stop
            merge these based on intermediate stops.

            :returns : merged dataframe.
        """
        first_trip = self.stop_times_df[
            self.stop_times_df.trip_id.isin(self.start_trips['trip_id']) & self.stop_times_df.stop_id.isin(
                self.onehop_set)]
        second_trip = self.stop_times_df[
            self.stop_times_df.trip_id.isin(self.end_trips['trip_id']) & self.stop_times_df.stop_id.isin(
                self.onehop_set)]

        # Remove redundant fields.
        first_trip = first_trip.drop(columns=['stop_sequence'])
        second_trip = second_trip.drop(columns=['stop_sequence'])

        first_trip.columns = ['first_trip_id', 'first_tp_arrival_time', 'first_tp_departure_time', 'stop_id']
        second_trip.columns = ['second_trip_id', 'second_tp_arrival_time', 'second_tp_departure_time', 'stop_id']

        result = pd.merge(first_trip, second_trip, how='inner', on='stop_id', left_index=False, right_index=False,
                          sort=True).drop(columns=['stop_id'], axis=1).to_dict(orient='records')

        return result
