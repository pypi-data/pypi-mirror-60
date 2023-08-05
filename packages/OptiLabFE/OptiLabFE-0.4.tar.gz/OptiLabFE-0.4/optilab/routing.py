import json
import gmaps
import ipywidgets as widgets
import geopy
import urllib.request

from optilab.module import Module
from optilab.optimizer import Optimizer


def create_distance_matrix(data):
    addresses = data["addresses"]
    API_key = data["API_key"]
    # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
    max_elements = 100
    num_addresses = len(addresses) # 16 in this example.
    # Maximum number of rows that can be computed per request (6 in this example).
    max_rows = max_elements // num_addresses
    # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    # Send q requests, returning max_rows rows per request.
    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)

    # Get the remaining remaining r rows, if necessary.
    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        distance_matrix += build_distance_matrix(response)
    return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        # Build a pipe-separated string of addresses
        address_str = ''
        for i in range(len(addresses) - 1):
          address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
                         dest_address_str + '&key=' + API_key
    with urllib.request.urlopen(request) as url:
        jsonResult = url.read()
    response = json.loads(jsonResult)
    return response

def build_distance_matrix(response):
    distance_matrix = []
    for row in response['rows']:
        row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    return distance_matrix

class RoutingWidget(Module):

    colors = [
        (255,   0,   0),  # red
        (0  , 100,   0),  # green
        (0  ,   0, 255),  # blue
        (0  , 255, 255),  # cyan
        (255,   0, 255),  # magenta
    ]

    def __init__(self, email='s@d.com', secret='12312kl3nk12b3n1b3', addr='127.0.0.1', port=8080, has_optim = True):

        # layout options
        max_layout = widgets.Layout(width = '99%')
        button_layout = widgets.Layout(width = '25px', height = '25px')

        # init gmaps
        self.API_KEY = 'AIzaSyCGOa79k466MIwCERz5_obRhmONuebj5Cs'
        gmaps.configure(api_key=self.API_KEY)

        # self.figure = gmaps.figure(zoom_level = 10, center = (33.4484, -112.0740))
        self.figure = gmaps.figure()
        self.drawing = gmaps.drawing_layer(show_controls = False)
        self.drawing.on_new_feature(self.on_new_feature)
        self.figure.add_layer(self.drawing)
        self.geocoder = geopy.geocoders.GoogleV3(api_key=self.API_KEY)
        self.marker_selection = widgets.ToggleButtons(
            options = ["Depot", "Dropoff"],
            description = "Add Marker:",
            disabled = False,
            layout = max_layout
        )
        self.marker_selection.observe(self.on_marker_selection, "value")
        self.drawing.marker_options = gmaps.MarkerOptions(label = "D")
        self.input_map = widgets.VBox([self.figure, self.marker_selection], layout = widgets.Layout(width = '70%'))

        ### Dropdowns

        # address dropdown
        self.address_dropdown = widgets.Dropdown(
            description = "Address",
        )
        self.address_dropdown.observe(self.on_address_selection, "value")
        self.demand_slider = widgets.IntSlider(
            min = 0,
            max = 50,
            description = "Demand:",
            disabled = True,
            readout = True,
            # readout_format = '.1f',
            layout = max_layout
        )
        self.demand_slider.observe(self.on_demand_selection, "value")
        sub_button = widgets.Button(description = '-', layout = button_layout)
        sub_button.on_click(self.on_sub_address)
        address_options = widgets.VBox([widgets.HBox([self.address_dropdown, sub_button], layout = max_layout), self.demand_slider])

        # vehicle dropdown
        self.vehicles = []
        self.vehicle_name = widgets.Text(
            description = "New Vehicle:",
            disabled = False,
        )
        add_button = widgets.Button(description = '+', layout = button_layout)
        add_button.on_click(self.on_add_vehicle)

        self.vehicle_dropdown = widgets.Dropdown(
            description = "Vehicle",
        )
        self.vehicle_dropdown.observe(self.on_vehicle_selection, "value")
        self.capacity_slider = widgets.IntSlider(
            min = 0,
            max = 50,
            description = "Capacity:",
            disabled = True,
            readout = True,
            # readout_format = '.1f',
            layout = max_layout
        )
        self.capacity_slider.observe(self.on_capacity_selection, "value")
        sub_button = widgets.Button(description = '-', layout = button_layout)
        sub_button.on_click(self.on_sub_vehicle)

        self.vehicle_options = widgets.VBox([widgets.HBox([self.vehicle_name, add_button], layout = max_layout),
                                        widgets.HBox([self.vehicle_dropdown, sub_button], layout = max_layout),
                                        self.capacity_slider],
                                        layout = widgets.Layout(margin = '100px 0px 0px 0px'))

        # run button
        run_button = widgets.Button(description = "RUN ROUTING", layout = widgets.Layout(margin = '35px auto auto auto'))
        run_button.on_click(self.on_run)

        self.dropdowns = widgets.VBox([address_options, self.vehicle_options, run_button],
                layout = widgets.Layout(width = '30%', margin = '100px 0px 100px 0px'))

        # final widget
        self.data = None
        self.widget = widgets.HBox([self.input_map, self.dropdowns])

        if has_optim:
            # setup optimizer
            self.optim = Optimizer()

            # Open a new session and connect to specified server
            self.optim.session(email=email, secret=secret, addr=addr, port=port)

            # Create an instance of a remote optimizer with 2 parallel workers
            self.opt_id = self.optim.get_optimizer(num_workers=2)

            # Load the instance into the optimizer
            self.optim.add_modules(self)

    def get_location_details(self, location):
        return self.geocoder.reverse(location, exactly_one=True)

    def display(self):
        return self.widget

    def vis_results(self, json_string):
        json_string = json_string.split(",\nmetrics")[0] + "}"
        res_data = json.loads(json_string)

        sol = res_data['objectiveValuesList']

        print("visualizing...")

        for i, v_data in enumerate(sol):
            route = v_data['route']
            locs = [(self.locations_geo[l_idx][0],
                     self.locations_geo[l_idx][1])
                    for l_idx in route]

            for n, (s, t) in enumerate(zip(locs, locs[1:])):
                if route[n] > 0:
                    self.drawing.features[route[n]].label = "%s #%i" % (self.vehicles[i]["name"], n)
                line = gmaps.Line(s, t, stroke_color = self.colors[i])
                self.drawing.features = self.drawing.features + [line]
            # origin_geo = self.locations_geo[route[0]]
            # origin = (origin_geo[0], origin_geo[1])
            # waypoints = [(self.locations_geo[l_idx][0],
            #               self.locations_geo[l_idx][1])
            #              for l_idx in route[1:-1]]
            # dest_geo = self.locations_geo[route[-1]]
            # dest = (dest_geo[0], dest_geo[1])
            # v_directions = gmaps.directions_layer(
            #         origin, dest, waypoints,
            #         travel_mode = 'DRIVING',
            #         stroke_color = self.colors[i])
            # self.figure.add_layer(v_directions)
            # print(self.figure)
        print("done")

    def get_options_from_features(self):
        if len(self.drawing.features) == 0:
            return []
        options = [(f.info["address"], i) for (i, f) in enumerate(self.drawing.features)]
        if self.drawing.features[0].label == 'D':
            options[0] = ("[DEPOT] %s" % self.drawing.features[0].info["address"], 0)
        return options

    def on_new_feature(self, feature):
        try:
            location = feature.location
        except AttributeError:
            return # Not a marker

        feature.info = {}
        is_depot = self.marker_selection.value == "Depot"
        if is_depot:
            self.drawing.features = [feature] + [f for f in self.drawing.features if f.label != 'D']
            feature.info["demand"] = 0
        else:
            feature.info["demand"] = 5
            if len(self.drawing.features) > 12:
                self.drawing.features = self.drawing.features[:-1]
        feature.info["location"] = location
        feature.info["address"] = self.get_location_details(location).address

        self.address_dropdown.options = self.get_options_from_features()
        self.address_dropdown.value = self.address_dropdown.options[0 if is_depot else -1][1]

    def on_address_selection(self, _):
        if len(self.drawing.features) == 0:
            return
        f = self.drawing.features[self.address_dropdown.value]
        if f.label == 'D':
            self.demand_slider.disabled = True
        else:
            self.demand_slider.disabled = False
        self.demand_slider.value = f.info["demand"]

    def on_sub_address(self, _):
        f_idx = self.address_dropdown.value
        if f_idx is None:
            return
        self.drawing.features = self.drawing.features[:f_idx] + self.drawing.features[f_idx+1:]
        self.address_dropdown.options = self.get_options_from_features()

    def on_demand_selection(self, _):
        if len(self.drawing.features) == 0:
            self.demand_slider.disabled = True
            self.demand_slider.value = 0.0
            return
        self.drawing.features[self.address_dropdown.value].info["demand"] = self.demand_slider.value

    def on_vehicle_selection(self, _):
        if len(self.vehicles) == 0:
            return
        self.capacity_slider.disabled = False
        v_idx = self.vehicle_dropdown.value
        self.capacity_slider.value = self.vehicles[v_idx]["capacity"]

    def on_add_vehicle(self, _):
        if self.vehicle_name.value not in [v["name"] for v in self.vehicles] and \
           self.vehicle_name.value != '' and \
           len(self.vehicles) <= 4:
            self.vehicles.append({"name" : self.vehicle_name.value, "capacity" : 15})
            self.vehicle_dropdown.options = [(v["name"], i) for (i, v) in enumerate(self.vehicles)]
            self.vehicle_name.value = ''
            self.vehicle_dropdown.value = self.vehicle_dropdown.options[-1][1]

    def on_sub_vehicle(self, _):
        if self.vehicle_dropdown.value is not None:
            v_idx = self.vehicle_dropdown.value
        else:
            return
        self.vehicles.pop(v_idx)
        self.vehicle_dropdown.options = [(v["name"], i) for (i, v) in enumerate(self.vehicles)]

    def on_capacity_selection(self, _):
        if len(self.vehicles) == 0:
            self.capacity_slider.disabled = True
            self.capacity_slider.value = 0.0
            return
        self.vehicles[self.vehicle_dropdown.value]["capacity"] = self.capacity_slider.value

    def on_marker_selection(self, change):
        marker_mode = self.marker_selection.value
        
        if marker_mode == "Depot":
            self.drawing.marker_options = gmaps.MarkerOptions(label = 'D')
        elif marker_mode == "Dropoff":
            self.drawing.marker_options = gmaps.MarkerOptions(label = '')
        else:
            raise ValueError("Unknown marker selection mode: %s" % marker_mode)

    def make_json(self, vehicles = None):

        if vehicles is None:
            vehicles = self.vehicles

        if len(vehicles) == 0 or \
           len(self.drawing.features) == 0 or \
           self.drawing.features[0].label != 'D':
            return

        self.locations_geo = [f.location for f in self.drawing.features]

        loc_data = {
            'addresses' : [str(f.info["location"][0]) + "," + str(f.info["location"][1]) for f in self.drawing.features],
            'API_key' : self.API_KEY
        }
        return {
            "framework" : "OR",
            "classType" : "VRP",
            "package" : "OR-TOOLS",
            "model" : "vrp_capacity_constraints",
            "demands" : [f.info["demand"] for f in self.drawing.features],
            "distance_matrix" : create_distance_matrix(loc_data),
            "num_vehicles" : len(vehicles),
            "vehicle_capacities" : [v["capacity"] for v in vehicles],
            "depot" : 0
        }

    def on_run(self, _):
        self.data = self.make_json()
        print(self.data)
        self.res = self.optim.solve()
        print(self.res)
        self.vis_results(self.res)

class Routing(Module):

    colors = [
        (255,   0,   0),  # red
        (0  , 100,   0),  # green
        (0  ,   0, 255),  # blue
        (0  , 255, 255),  # cyan
        (255,   0, 255),  # magenta
    ]

    def __init__(self, name):
        self.name = name
        self.locations = []
        self.distance_matrix = None
        self.data = {
            "framework" : "OR",
            "classType" : "VRP",
            "package" : "OR-TOOLS",
            "model" : "vrp_capacity_constraints",
            "demands" : None,
            "distance_matrix" : None,
            "num_vehicles" : None,
            "vehicle_capacities" : None,
            "num_vehicles" : None,
            "depot" : None
        }

        # google maps configuration
        self.API_KEY = 'AIzaSyCGOa79k466MIwCERz5_obRhmONuebj5Cs'
        gmaps.configure(api_key = self.API_KEY)
        self._geocoder = geopy.geocoders.GoogleV3(api_key=self.API_KEY)

    def set_vehicles(self, capacities):
        self.data['num_vehicles'] = len(capacities)
        self.data['vehicle_capacities'] = capacities

    def set_locations(self, locations, demands, depot = 0):
        assert len(locations) == len(demands)
        # TODO: look for more configurable solution to mapping natural
        # language address string to valid json string.
        self.locations = [l.replace(' ', '+') for l in locations]
        self.locations_geo = [self.geocode(l) for l in locations]

        # set local data
        self.data['depot'] = depot
        self.data['demands'] = demands

        # distance matrix is invalid, set to None
        self.data['distance_matrix'] = None

    def geocode(self, loc):
        return self._geocoder.geocode(loc)

    def load_result(self, json_string):
        res_data = json.loads(json_string)

        print("Model:", res_data['modelId'])
        print("Status:", res_data['modelStatus'])
        print("Overall Distance:", res_data['totDistanceAllRoutes'])
        print("Overall Load:", res_data['totLoadAllRoutes'])
        print("--------------------------------------------------\n")

        sol = res_data['objectiveValuesList']
        for v_data in sol:
            print("VEHICLE", v_data['vehicleId'])
            print("Route:", v_data['route'])
            print("Load:", v_data['load'])
            print("Total Vehicle Distance:", v_data['totRouteDistance'])
            print("Total Vehicle Load:", v_data['totRouteLoad'])
            print()

    def vis_results(self, json_string):
        json_string = json_string.split(",\nmetrics")[0] + "}"
        res_data = json.loads(json_string)

        fig = gmaps.figure()
        sol = res_data['objectiveValuesList']

        for i, v_data in enumerate(sol):
            route = v_data['route']
            origin_geo = self.locations_geo[route[0]]
            origin = (origin_geo.latitude, origin_geo.longitude)
            waypoints = [(self.locations_geo[l_idx].latitude,
                          self.locations_geo[l_idx].longitude)
                         for l_idx in route[1:-1]]
            dest_geo = self.locations_geo[route[-1]]
            dest = (dest_geo.latitude, dest_geo.longitude)
            v_directions = gmaps.directions_layer(
                    origin, dest, waypoints,
                    travel_mode = 'DRIVING',
                    stroke_color = self.colors[i])
            fig.add_layer(v_directions)

        return fig

    def load_from_json(self, jsonfile):
        data = json.load(open(jsonfile))
        assert len(data['vehicle_capacities']) == data['num_vehicles']
        N = len(data['demands'])
        assert (len(data['distance_matrix']), len(data['distance_matrix'][0])) == \
               (N,                    N                                      )  # each node has a demand
        assert data['depot'] < N                                                # the depot is a node id
        self.data = data

    def get_json(self):
        if self.data['distance_matrix'] is None:
            loc_data = {
                'addresses' : self.locations,
                'API_key' : self.API_KEY
            }
            self.data['distance_matrix'] = create_distance_matrix(loc_data)
        return self.data

# FULL PROBLEM INSTANCE
# # # # # # # # # # # #
#
# # Define the problem instance
# routing_demo.set_locations(['3610 Hacks Cross Rd Memphis TN', # depot
#                             '1921 Elvis Presley Blvd Memphis TN',
#                             '149 Union Avenue Memphis TN',
#                             '1034 Audubon Drive Memphis TN',
#                             '1532 Madison Ave Memphis TN',
#                             '706 Union Ave Memphis TN',
#                             '3641 Central Ave Memphis TN',
#                             '926 E McLemore Ave Memphis TN',
#                             '4339 Park Ave Memphis TN',
#                             '600 Goodwyn St Memphis TN',
#                             '2000 North Pkwy Memphis TN',
#                             '262 Danny Thomas Pl Memphis TN',
#                             '125 N Front St Memphis TN',
#                             '5959 Park Ave Memphis TN',
#                             '814 Scott St Memphis TN',
#                             '1005 Tillman St Memphis TN'
#                            ], demands = [0, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8])
# routing_demo.set_vehicles(capacities = [15, 15, 15, 15])
