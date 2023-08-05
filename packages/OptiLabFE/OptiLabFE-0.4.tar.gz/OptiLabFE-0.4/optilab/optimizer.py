import requests
import time
import json


class Optimizer():

    optimizer_id = None
    _secret_key = None
    email = None
    model = []
    flow  = []
    nodes = 0
    modules = []
    moduledicts = []
    model_data = None
    address = "127.0.0.1"
    port = 8080

    def session(self, email=None, secret=None, addr=None, port=None):
        """Initialize session by logging with email address and
        secret key that was used during registration"""

        email_flag = False
        if email == None and self.email == None:
            email_flag = True
            self.email = input('Enter email address: ')
        elif email != 1 and self.email == None:
            email_flag = True
            self.email = email

        if secret == None and self._secret_key == None:
            if not email_flag:
                print("Using email: " + self.email)

            secret = input('Enter secret : ')
            self._secret_key = secret
        elif secret != None and self._secret_key == None:
            self._secret_key = secret

        if addr is not None:
            self.address = addr

        if port is not None:
            self.port = port

        print("Verifying keys...")
        #time.sleep(1)
        if(True):
            #self.email=email
            #self.secret_key = secret
            print('Verified')
        else:
            print("Invalid secret key")

    def get_optimizer(self, num_workers=None):
        """Get unique optimizer id for subsequent API calls"""
        if self._secret_key == None:
            return "Please initialize session first"

        url = "http://" + self.address + ":" + str(self.port) + "/optimizer"
        optimizer_json = json.loads(requests.get(url).text)

        # if num_workers is None:
        #     print('Using default number of worker: 1')
        # if num_workers > 4:
        #     print ('Exceeding number of worker, using number of workers: 4')

        self.optimizer_id = optimizer_json["optimizer"]
        return self.optimizer_id

    def get_last_model(self, url = 'https://optilabtech-mock.herokuapp.com/result' ):
        if url == 'https://optilabtech-mock.herokuapp.com/result':
            print('Using mock server ...')
        else:
            print("GET request to URL: " + url)
        return requests.get(url).text

    def _remove_directions(self,mod):
        mod.left=None
        mod.right=None
        mod.comband=None
        mod.combor=None
        return mod

    def get_modeldata(self):
        if self.modules[0].combor is None:
            self.model_data = self.modules[0].get_json()
        else:
            # Create combinator
            base_model_1 = self.modules[0]
            base_model_2 = self.modules[0].combor

            # Remove directions
            base_model_1.combor = None
            base_model_2.combor = None

            # Create dictionaries
            model_1 = base_model_1.get_json()
            model_2 = base_model_2.get_json()

            # Set IDs corresponding to the name of the models
            model_1['id'] = model_1['name']
            model_2['id'] = model_2['name']

            # Create a dictionary to translate into JSON combinator model
            comb_model = {};
            comb_model['framework'] = "Connectors"
            comb_model['classType'] = "Combinator"
            comb_model['id'] = "combinator"

            # List of IDs for the combinator modules
            comb_obj_ids = []
            comb_obj_ids.append(model_1["id"])
            comb_obj_ids.append(model_2["id"])
            comb_model['combinatorObjects'] = comb_obj_ids

            # Combinator objects (JSONs)
            objs_list = []
            objs_list.append(model_1)
            objs_list.append(model_2)
            comb_model['objectsList'] = objs_list
            self.model_data = comb_model

        #{
        #'modules':[{mod.name: mod.get_json() for mod in self.modules}],
        #'model' :self.model,
        #'email':self.email,
        #'secret_key':self._secret_key,
        #'nodes':self.nodes,
        #'optimizer':self.optimizer_id
        #}

    def cleanup(self, optimizer_id):
        # Check for the optimizer id
        assert optimizer_id != None, 'Provide a valid optimizer ID'

        url = "http://" + self.address + ":" + str(self.port) + "/optimizer"
        url += "/" + optimizer_id

        #  http://127.0.0.1:8080/optimizer/123ab5t
        requests.request("DELETE", url)

    def solve(self):
        """POST model data to /model API"""
        assert self.optimizer_id != None, 'Get optiSmizer id using .get_optimizer first!'

        # Load the data
        self.get_modeldata()

        #Clean up before writing json
        self.modules = [self._remove_directions(mod) for mod in self.modules]

        #url = "http://127.0.0.1:8080/model"
        url = "http://" + self.address + ":" + str(self.port) + "/model"
        url += "/" + self.optimizer_id

        # Create the payload and send request to server
        payload = json.dumps(self.model_data)
        #print ("payload:")
        #print (payload)
        #return ""
        headers = {'Accept': "application/json",'Content-Type': "application/json",}
        response = requests.request("POST", url, data=payload, headers=headers)

        return response.text

    def build_graph(self,*argv):
        """ try cp1 >> mip1, mip2 << cp2, mip2 | mip1 as arguments"""
        print(locals())
        print('000')
        print(globals())
        for exp in argv:
            eval(exp,globals())
            self.flow.append(exp)

    def generate_model(self):
        for mod in self.modules:
            self.model.append({mod.name : {
                'left':None if mod.left == None else mod.left.name,
                'right':None if mod.right == None else mod.right.name,
                'and':None if mod.comband == None else mod.comband.name,
                'or':None if mod.combor == None else mod.combor.name}})
            self.nodes = self.nodes+1 #this is a count of nodes traversed


    def add_modules(self, *argv):
        for mod in argv:
            self.modules.append(mod)
            self.moduledicts.append(mod.get_json())

        self.generate_model()
