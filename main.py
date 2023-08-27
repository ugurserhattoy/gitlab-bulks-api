from flask import Flask
from flask_restful import Api, Resource, reqparse
import os
import gitlab
from ProjectListOp import ProjectListFuncs
from SetThingsUp import SetThingsUp
from dotenv import load_dotenv

load_dotenv()

gl = gitlab.Gitlab(url=os.getenv('GLAB_URL'), private_token=os.getenv('PRIVATE_TOKEN'))
gl.auth()
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('id', type=int)
parser.add_argument('group') # group path
parser.add_argument('ppath') # project path
parser.add_argument('idList', action='append')
parser.add_argument('input') # input for setting

project_list = {}

ProjectListFunction = ProjectListFuncs(gl, project_list)
SetThings = SetThingsUp(gl)

class ProjectListOps(Resource):
    def get(self):
        return project_list
    
    def put(self):
        args = parser.parse_args()
        if args['id']:
            p = ProjectListFunction.getProjectById(args['id'])
            ProjectListFunction.putProjectArgs(p)
            return {str(p.id): project_list[p.id]}
        elif args['group']:
            ProjectListFunction.putProjectsByGroup(args['group'])
            return project_list
    
    def delete(self):
        project_list.clear()

class UpdateSomething(Resource):
    def __init__(self):
        args = parser.parse_args()
        self.proj_list = args['idList']
        self.input = args['input']
    
    def put(self, setting):
        response = getattr(SetThings, setting)(self.input, self.proj_list)
        return response
    
    def delete(self, setting):
        if setting == 'protectedBranches':
            response = SetThings.removeBranchProtection(self.input, self.proj_list)
            return response
        else:
            return({'Error': 'Method Not Allowed'}, 405)
            
api.add_resource(ProjectListOps, '/projectlist', methods=['GET', 'PUT', 'DELETE'])
api.add_resource(UpdateSomething, '/projectlist/<string:setting>', methods=['PUT', 'DELETE'])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)