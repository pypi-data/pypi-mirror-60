import json
import ipysheet
import ipywidgets as widgets
import gmaps
import numpy as np

from optilab import *
from optilab.module import Module


class SchedulingToRouting(Module):
    """ Coordinates all synchronization between a scheduling and routing widget. """

    def __init__(self, scheduler, router, email='s@d.com', secret='12312kl3nk12b3n1b3', addr='127.0.0.1', port=8080):
        self.scheduler = scheduler
        self.router = router

        self.upload_button = widgets.FileUpload(
            description = "Upload JSON",
            accept = ".json",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple = False   # True to accept multiple files upload else False
        )
        self.upload_button.observe(self.on_upload, 'value')

        vo = self.router.vehicle_options
        v_dropdown = vo.children[1].children[1]
        v_dropdown_without_sub_button = vo.children[1].children[0]
        v_dropdown_without_sub_button.layout = vo.children[1].layout
        reduced_vo = widgets.VBox([
            v_dropdown_without_sub_button,
            vo.children[2]],
            layout = vo.layout
        )

        self.data = None
        self.widget = reduced_vo

        # setup optimizer
        self.optim = Optimizer()

        # Open a new session and connect to specified server
        self.optim.session(email=email, secret=secret, addr=addr, port=port)

        # Create an instance of a remote optimizer with 7 parallel workers
        self.opt_id = self.optim.get_optimizer(num_workers=7)

        # Load the instance into the optimizer
        self.optim.add_modules(self)

    def display(self):
        self.scheduler_widget = self.scheduler.display()
        # self.transformer_widget = self.widget
        self.router_widget = self.router.display()
        
        self.scheduler_widget.layout.padding = '10px 10px 10px 10px'
        self.scheduler_widget.layout.margin = '0 0 10px 0'
        self.scheduler_widget.layout.border = "1px solid red"

        self.scheduler_widget.children = (self.upload_button,) + self.scheduler_widget.children[1:]

        # self.transformer_widget.layout.padding = '10px 10px 10px 10px'
        # self.transformer_widget.layout.margin = '0 0 10px 0'
        # self.transformer_widget.layout.border = "1px solid red"

        self.router_widget.layout.padding = '10px 10px 10px 10px'
        self.router_widget.layout.border = "1px solid red"

        run_button = widgets.Button(description = "RUN PIPELINE")
        run_button.layout.margin = '10px 0 0 0'
        run_button.on_click(self.on_run)

        self.res_widget = widgets.HBox()
        self.full_widget = widgets.VBox([ 
            self.scheduler_widget,
            # transformer_widget,
            self.router_widget,
            run_button,
            self.res_widget
        ])

        self.full_widget.layout.padding = '10px 10px 10px 10px'
        self.full_widget.layout.border = "1px solid black"

        return self.full_widget

    def on_upload(self, _):
        json_string = list(self.upload_button.value.values())[0]["content"]
        self.data = json.loads(json_string.decode('utf-8'))
        self.scheduler.num_days.value = self.data["num_days"]
        self.scheduler.shifts_per_day.value = self.data["num_shifts"]

        for p, r in zip(self.data["personnel_names"], self.data["shift_requests"]):
            self.scheduler.name_box.value = p
            labeled_sheet = self.scheduler.new_sheet(ipysheet.numpy_loader.from_array(np.array(r).T.astype(np.bool)))
            self.scheduler.add_sheet(labeled_sheet)

            self.router.vehicles.append({"name" : p, "capacity" : 15})
            self.router.vehicle_dropdown.options = [(v["name"], i) for (i, v) in enumerate(self.router.vehicles)]
            self.router.vehicle_name.value = ''
            self.router.vehicle_dropdown.value = self.router.vehicle_dropdown.options[-1][1]

    def on_run(self, _):

        # get scheduler output
        self.data = self.scheduler.make_json()
        scheduler_res = self.optim.solve()
        self.scheduler.res_widget = self.scheduler.vis_results(scheduler_res)
        self.scheduler.widget.children = self.scheduler.widget.children[:-1] + (self.scheduler.res_widget,)
        self.scheduler_widget.layout.border = "1px solid green"

        routes_table = widgets.Tab()
        scheduler_res = scheduler_res.split(",\nmetrics")[0] + "}"
        res_data = json.loads(scheduler_res)
        data = res_data["objectiveValuesList"]

        # transform scheduler json to combinator problem instance
        objects_list = []

        for day_data in data:
            d = day_data["day"]
            figure = gmaps.figure(zoom_level = 10, center = (33.4484, -112.0740))
            drawing = gmaps.drawing_layer(show_controls = False)
            for f in self.router.drawing.features:
                f_copy = gmaps.Marker(location = f.location, label = f.label)
                drawing.features = drawing.features + [f_copy]
            figure.add_layer(drawing)
            routes_table.children = routes_table.children + (figure,)
            routes_table.set_title(len(routes_table.children) - 1, "Day %i" % (d + 1))
            vehicles = []
            v_idx = []
            for (p_idx, s, request_satisfied) in day_data["shifts"]:
                v_idx.append(p_idx)
                vehicles.append(self.router.vehicles[p_idx])
            routing_json = self.router.make_json(vehicles)
            routing_json["use_file_descriptors"] = False
            routing_json["id"] = "r%i" % (d + 1)
            routing_json["model"] = routing_json["id"]

            self.data = routing_json
            routing_res = self.optim.solve()
            print("DAY %i RESULTS:" % (d + 1))
            print(routing_res)
            # objects_list.append(routing_json)

            routing_res = routing_res.split(",\nmetrics")[0] + "}"
            res_data = json.loads(routing_res)

            sol = res_data['objectiveValuesList']
            for i, v_data in zip(v_idx, sol):
                route = v_data['route']
                locs = [(self.router.locations_geo[l_idx][0],
                         self.router.locations_geo[l_idx][1])
                        for l_idx in route]

                for n, (s, t) in enumerate(zip(locs, locs[1:])):
                    if route[n] > 0:
                        drawing.features[route[n]].label = "%s #%i" % (self.router.vehicles[i]["name"], n)
                    line = gmaps.Line(s, t, stroke_color = self.router.colors[i])
                    drawing.features = drawing.features + [line]

        self.router_widget.layout.border = "1px solid green"
        self.res_widget = routes_table
        self.full_widget.children = self.full_widget.children[:-1] + (self.res_widget,)

        # self.data = {
        #     "framework": "Connectors",
        #     "classType": "Combinator",
        #     "id": "combinator",
        #     "combinatorLogic": "collect_all",
        #     "combinatorObjects": [rj["id"] for rj in objects_list],
        #     "objectsList" : objects_list
        # }

        # print(self.data)

        # self.res = self.optim.solve()
        # print()
        # print("results:")
        # print(self.res)
