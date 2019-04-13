from flask import Flask, render_template, url_for, flash, redirect, request
from gtfs import GTFS


app = Flask(__name__)
# SECRET KEY Generated using secrets module // secrets.token_hex()
app.config['SECRET_KEY'] = 'b788d08ada31337f93eb7743dd64f6f4'

# configure the route paths
app.config['routes_path'] = './gtfs/routes.txt'
app.config['stops_path'] = './gtfs/stops.txt'
app.config['stops_times_path'] = './gtfs/stop_times.txt'
app.config['trips_path'] = './gtfs/trips.txt'

# Setup GTFS
gtfs = GTFS(app.config['routes_path'],
            app.config['stops_path'],
            app.config['stops_times_path'],
            app.config['trips_path'])


@app.route('/', methods=['GET', 'POST'])
def get_routes():
    if request.form:
        form = request.form

        # if start stop not selected by the user, return error message
        try:
            form['start stop']
        except:
            flash(f'Please select a start stop!', 'warning')
            # name of the function for the route
            return render_template('routes_form.html', title='Find Routes', stops=gtfs.stop_names_id)

        # if end stop not selected by the user, return error message
        try:
            form['end stop']
        except:
            flash(f'Please select a end stop!', 'warning')
            return render_template('routes_form.html', title='Find Routes', stops=gtfs.stop_names_id)

        start_stop = form['start stop']
        end_stop = form['end stop']

        # If picked start and end stops are same, give a warning message to user
        if start_stop == end_stop:
            flash(f'Same stops entered for finding routes, please choose diff stops!', 'warning')
            # name of the function for the route
            return render_template('routes_form.html', title='Find Routes', stops=gtfs.stop_names_id)

        flash(f'Request for routes submitted successfully: ({start_stop} -> {end_stop})', 'success')
        # get the stops from stop_name_ids
        start = gtfs.get_stop_from_stop_name_id(start_stop)
        end = gtfs.get_stop_from_stop_name_id(end_stop)
        # find zero hop trips
        gtfs.zero_hop(start['stop_id'], end['stop_id'])
        # find one hop trips
        gtfs.one_hop(start['stop_id'], end['stop_id'])

        zerohop = gtfs.zerohop_trips()
        onehop = gtfs.onehop_trips()

        total_onehop_results = len(onehop)
        total_zerohop_results = len(zerohop)


        ## Get first max(len, 50) zero hop trips
        zerohop_res = list()
        count = 0
        for val in zerohop:
            print(val)
            zerohop_res.append(val)
            count +=1
            if count > 49:
                break

        ## Get first max(len, 50) one hop trips
        if len(onehop)>50:
            onehop = onehop[0:50]

        return render_template('layout.html', title='Find Routes', stops=gtfs.stop_names_id,
                               zerohop_result=zerohop_res, onehop_result=onehop[0:50],
                               total_onehop_results = total_onehop_results, total_zerohop_results= total_zerohop_results)

    return render_template('layout.html', title='Find Routes', stops=gtfs.stop_names_id)


if __name__ == '__main__':
    app.run(debug=True)
