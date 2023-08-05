import json
import ipysheet
import ipywidgets as widgets
import numpy as np

from optilab.module import Module
from optilab.optimizer import Optimizer

class SchedulingWidget(Module):

    def __init__(self, email='s@d.com', secret='12312kl3nk12b3n1b3', addr='127.0.0.1', port=8080, has_optim = True):

        # upload button
        self.upload_button = widgets.FileUpload(
            description = "Upload JSON",
            accept = ".json",  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple = False   # True to accept multiple files upload else False
        )
        self.upload_button.observe(self.on_upload, 'value')

        # scheduling info
        self.num_days = widgets.BoundedIntText(
            value=7,
            min=1,
            max=30,
            step=1,
            description='# of Days:',
            disabled=False
        )
        self.shifts_per_day = widgets.BoundedIntText(
            value=3,
            min=1,
            max=24,
            step=1,
            description='Shifts/Day:',
            disabled=False
        )

        self.schedule_info = widgets.VBox([self.num_days, self.shifts_per_day])

        ### add personnel
        self.name_box = widgets.Text(
            placeholder='Enter name here',
            description='Name:',
            disabled=False
        )
        self.button_layout = widgets.Layout(width = '25px', height = '25px')
        self.add_button = widgets.Button(description = '+', layout = self.button_layout)
        self.add_button.on_click(self.on_add_personnel)

        self.add_personnel = widgets.HBox([self.name_box, self.add_button])


        # sheet = ipysheet.sheet(rows = shifts_per_day.value,
        #                        row_headers = ["Shift %i" % (s + 1) for s in range(shifts_per_day.value)],
        #                        columns = num_days.value,
        #                        column_headers = ["Day %i" % (d + 1) for d in range(num_days.value)])

        # add logic for schedule tabs
        self.schedules = widgets.Tab()
        self.num_days.observe(self.on_schedule_change, names = "value")
        self.shifts_per_day.observe(self.on_schedule_change, names = "value")

        run_button = widgets.Button(description = "RUN SCHEDULING")
        run_button.on_click(self.on_run)

        # final widget
        self.data = None
        self.res_widget = widgets.HBox()
        self.widget = widgets.VBox([self.upload_button,
                                    self.schedule_info,
                                    self.add_personnel,
                                    self.schedules,
                                    run_button,
                                    self.res_widget])

        if has_optim:
            # setup optimizer
            self.optim = Optimizer()

            # Open a new session and connect to specified server
            self.optim.session(email=email, secret=secret, addr=addr, port=port)

            # Create an instance of a remote optimizer with 2 parallel workers
            self.opt_id = self.optim.get_optimizer(num_workers=2)

            # Load the instance into the optimizer
            self.optim.add_modules(self)

    def get_personnel(self):
        return [self.schedules.get_title(i) for i in range(len(self.schedules.children))]

    def display(self):
        return self.widget

    def new_sheet(self, sheet = None):
        if sheet is None:
            sheet = ipysheet.sheet()
        sheet.rows = self.shifts_per_day.value
        sheet.row_headers = ["Shift %i" % (i + 1) for i in range(sheet.rows)]
        sheet.columns = self.num_days.value
        sheet.column_headers = ["Day %i" % (i + 1) for i in range(sheet.columns)]
        return sheet

    def add_sheet(self, sheet):
        # define sub button
        sub_button = widgets.Button(description = '-', layout = self.button_layout)
        sub_button.on_click(self.on_sub_personnel)

        # add new sheet to the end
        content = widgets.VBox([sheet, sub_button])
        self.schedules.children = self.schedules.children + (content,)
        self.schedules.set_title(len(self.schedules.children) - 1, self.name_box.value)


    ### EVENT HANDLERS

    def on_upload(self, _):
        json_string = list(self.upload_button.value.values())[0]["content"]
        self.data = json.loads(json_string.decode('utf-8'))
        self.num_days.value = self.data["num_days"]
        self.shifts_per_day.value = self.data["num_shifts"]

        for p, r in zip(self.data["personnel_names"], self.data["shift_requests"]):
            self.name_box.value = p
            labeled_sheet = self.new_sheet(ipysheet.numpy_loader.from_array(np.array(r).T.astype(np.bool)))
            self.add_sheet(labeled_sheet)

    def on_add_personnel(self, _):
        print("here")
        if self.name_box.value not in self.get_personnel():

            # define sheet
            sheet = self.new_sheet()
            for d in range(self.num_days.value):
                for s in range(self.shifts_per_day.value):
                    ipysheet.cell(s, d, value = False)

            self.add_sheet(sheet)

        # switch focus to tab if this is the first
        if self.schedules.selected_index is None:
            self.schedules.selected_index = 0

    def on_sub_personnel(self, _):
        i = self.schedules.selected_index
        for j in range(i + 1, len(self.schedules.children)):
            # shift names to the left
            self.schedules.set_title(j - 1, self.schedules.get_title(j))
        # delete selected child
        self.schedules.children = self.schedules.children[:i] + self.schedules.children[i+1:]

    def on_schedule_change(self, change):

        new_children = []

        for content in self.schedules.children:
            old_sheet = content.children[0]
            new_sheet = self.new_sheet()

            # demon logic from hell, probably can be made more efficient using cell ranges.
            for d in range(self.num_days.value):
                for s in range(self.shifts_per_day.value):
                    if d >= old_sheet.columns or s >= old_sheet.rows:
                        ipysheet.cell(s, d, value = False)
                    else:
                        ipysheet.cell(s, d, value = old_sheet[s,d].value)
            new_children.append(widgets.VBox([new_sheet, content.children[1]]))

        self.schedules.children = new_children

    def vis_results(self, json_string):
        json_string = json_string.split(",\nmetrics")[0] + "}"
        res_data = json.loads(json_string)
        data = res_data["objectiveValuesList"]
        sheet = self.new_sheet()
        for day_data in data:
            d = day_data["day"]
            for (p_idx, s, request_satisfied) in day_data["shifts"]:
                ipysheet.cell(s, d, self.personnel_names[p_idx],
                              background_color = "green" if request_satisfied else "red")
        return sheet

    def make_json(self):

        if len(self.schedules.children) == 0:
            return

        data = {
            "framework" : "OR",
            "classType" : "SCHEDULING",
            "package" : "OR-TOOLS",
            "model" : "scheduling_example",
            "num_personnel" : len(self.schedules.children),
            "num_shifts" : self.shifts_per_day.value,
            "num_days" : self.num_days.value,
            "shift_requests" : []
        }
        self.personnel_names = self.get_personnel()

        for content in self.schedules.children:
            sheet = content.children[0]
            r = ipysheet.numpy_loader.to_array(sheet).T
            data["shift_requests"].append(r.astype(np.uint8).tolist())

        return data

    def on_run(self, _):

        self.data = self.make_json()
        self.res = self.optim.solve()
        self.res_widget = self.vis_results(self.res)
        self.widget.children = self.widget.children[:-1] + (self.res_widget,)

    def __del__(self):
        self.optim.cleanup(self.opt_id)


class Scheduling(Module):

    colors = ['red', 'blue', 'green', 'orange', 'yellow']

    def __init__(self, name):
        self.name = name
        self.personnel_names = []
        self.data = {
            "framework" : "OR",
            "classType" : "SCHEDULING",
            "package" : "OR-TOOLS",
            "model" : "scheduling_example",
            "num_personnel" : None,
            "num_shifts" : None,
            "num_days" : None,
            "shift_requests" : None
        }

        self.widget = SchedulingWidget()

    def display_widget(self):
        return self.widget.display()

    def add_schedule(self, num_days, num_shifts):
        self.data["num_days"] = num_days
        self.data["num_shifts"] = num_shifts

    def add_personnel(self, *personnel):
        if self.data["num_days"] is None or self.data["num_shifts"] is None:
            raise ValueError("Adding personnel to a non-existent schedule.")

        self.personnel_names = []
        all_shift_requests = []
        for p_data in personnel:
            name = p_data["name"]
            self.personnel_names.append(name)
            p_shift_requests = p_data["shift_requests"]
            one_hot_p_shift_requests = []
            if len(p_shift_requests) != self.data["num_days"]:
                raise ValueError("Invalid request for %s: %i days requested while %i scheduled"
                                 % (name, len(p_shift_requests), self.data["num_days"]))
            for s in p_shift_requests:
                request = [0] * self.data["num_shifts"]
                if s is not None:
                    if s <= 0 or s > self.data["num_shifts"]:
                        raise ValueError("Invalid request for %s: shift %i requested while only 1 - %i scheduled"
                                         % (name, s, self.data["num_shifts"]))
                    request[s-1] = 1
                one_hot_p_shift_requests.append(request)
            all_shift_requests.append(one_hot_p_shift_requests)

        self.data["num_personnel"] = len(personnel)
        self.data["shift_requests"] = all_shift_requests

    def load_result(self, json_string):
        res_data = json.loads(json_string)
        print(res_data)

    def vis_results(self, json_string):
        res_data = json.loads(json_string)
        data = res_data["objectiveValuesList"]
        sheet = ipysheet.sheet(rows = self.data["num_shifts"],
                               row_headers = ["Shift %i" % (s + 1) for s in range(self.data["num_shifts"])],
                               columns = self.data["num_days"],
                               column_headers = ["Sun", "Mon", "Tues", "Wed", "Thur", "Fri", "Sat"])
        for day_data in data:
            d = day_data["day"]
            for (p_idx, s, request_satisfied) in day_data["shifts"]:
                ipysheet.cell(s, d, self.personnel_names[p_idx])

        return sheet

example_response = json.dumps({
  "modelId": "scheduling_example",
  "modelStatus": "satified",
  "objectiveValuesList": [
      {
            "day": 0,
            "shifts":[
                    [1, 0, 0], [2, 1, 1], [3, 2, 1]
                  ],
      },
      {
            "day": 1,
            "shifts":[
                    [0, 0, 0], [2, 1, 1], [4, 2, 1]
                  ],
      },
      {
            "day": 2,
            "shifts":[
                    [1, 2, 0], [3, 0, 1], [4, 1, 1]
                  ],
      },
      {
            "day": 3,
            "shifts":[
                    [2, 0, 1], [3, 1, 1], [4, 2, 0]
                  ],
      },
      {
            "day": 4,
            "shifts":[
                    [0, 2, 1], [1, 0, 1], [4, 1, 0]
                  ],
      },
      {
            "day": 5,
            "shifts":[
                    [0, 2, 0], [2, 1, 1], [3, 0, 1]
                  ],
      },
      {
            "day": 6,
            "shifts":[
                    [0, 1, 0], [1, 2, 1], [4, 0, 0]
                  ],
          }
    ]
})
