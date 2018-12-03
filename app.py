from flask import Flask, Blueprint
from flask_restplus import Api, Resource, fields

import os, json
from os import listdir
from os.path import isfile, join

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='1.1', title='ESB Services API', description='A simple Services API.', doc='/doc') # to disable SwaggerUI add the following: , doc=False
app.register_blueprint(blueprint)

# Namespace:
ns = api.namespace('services', description='Service operations')

# Model:
a_service = api.model('Service_List', {'name' : fields.String(required=True, description='The service name.')})
b_service = api.model('Service', {'name' : fields.String(required=True, description='The service name.'),
                                  'command' : fields.String(required=True, description='The command to execute.')})

#####################
# Auxiliary Function ###########################################################
######################
def filesInDir():
    # Returns a dictionary of files inside "services/" folder.
    res = [f for f in listdir('services/') if isfile(join('services/', f))]
    return res

def fileNamesInDir():
    # Returns a dictionary of filenames, without ".json" extension.
    res = []
    for f in listdir('services/'):
        if isfile(join('services/', f)):
            res.append(f[:-5])
    return res

def check_service_existence(s_name):
    res = fileNamesInDir()
    if s_name in res:
        return True
    else:
        return None

######################
# Main Program       ###########################################################
######################

#EndPoint: /services
@ns.route('/')
class ServiceList(Resource):
    '''Shows a list of services and lets you POST to add new services'''
    # @api.marshal_with(a_service)
    @ns.marshal_list_with(a_service)
    def get(self):
        '''List all services'''
        onlyfiles = filesInDir()
        services = []

        for p in onlyfiles:
            if p.endswith('.json'):
                data = {'name': p[:-5]}
                # res["services"].append(data)
                services.append(data)
        print(services)
        return services, 200

    @ns.expect(b_service)
    @ns.marshal_with(b_service, code=201)
    def post(self):
        '''Create a new service'''
        onlyfiles = filesInDir() # List of files in 'services/' folder
        args = api.payload # Arguments received in POST JSON
        filename = args['name'] + str('.json') # 'serviceX.json' format file.

        if filename not in onlyfiles:
            print("File Dir: " + str(filename))
            with open(os.path.join("services", filename), 'w') as f:
                json.dump(args, f)
                return {"msg": "Service added", "service_data": args}, 201

        else:
            return {"msg": "The specified service already exists."}, 422

#EndPoint: /services/<string:service_name>
@ns.route('/<string:service_name>')
@ns.response(404, 'Service not found')
class Service(Resource):
    '''Show a single service item and lets you delete them'''
    @ns.doc('get_service')
    @ns.marshal_with(b_service)
    def get(self, service_name):
        '''Fetch a given service'''
        service = check_service_existence(service_name)
        if service:
            with open(os.path.join("services", service_name + str('.json'))) as f:
                data = json.load(f)
                return data
        else:
            return {"error": "Service not found."}, 404

    @ns.expect(b_service)
    @ns.marshal_with(b_service)
    def put(self, service_name):
        '''Update a service given its service name'''
        args = api.payload # Arguments received in PUT JSON
        filename = service_name + str('.json') # 'serviceX.json' format file.
        if os.path.exists(os.path.join("services", service_name + str('.json'))):
            with open(os.path.join("services", filename), 'w') as f:
                json.dump(args, f)
                return {"msg": "Service updated", "service_data": args}
        else:
            return {"error": "Service not found."}, 404

    @ns.response(204, 'Service deleted')
    def delete(self, service_name):
        '''Delete a service given its service name'''
        service = check_service_existence(service_name)
        # print("Service Name: " + str(service_name))
        # if service:
        if os.path.exists(os.path.join("services", service_name + str('.json'))):
            os.remove(os.path.join("services", service_name + str('.json')))
            return {"message": "Service deleted."}, 204
        else:
            return {"error": "Service not found"}, 404

if __name__ == '__main__':
    app.run(debug=True)
