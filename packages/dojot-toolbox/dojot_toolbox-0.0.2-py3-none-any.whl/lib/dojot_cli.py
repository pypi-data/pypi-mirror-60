import json
import os
import time
import yaml
import sys
import getpass
from termcolor import colored
from pyfiglet import Figlet
from . import Gui, Cron, Repository, K8sCLI
from .ansible_cli import AnsibleCLI
from .constants import installer as constants

# TODO: fazer testes na classe toda
class DojotCLI():
    def __init__(self, argv):
        self.vars = {}
        self.argv = argv
        self.ansible_cli = AnsibleCLI()
        self.k8s_cli = K8sCLI()

    def check_requirements(self):
        if not self.k8s_cli.is_installed():
            self.say_k8s_not_installed()
            self.say_thanks()
            sys.exit()

    def should_configure(self):
        if len(self.argv) == 2:
            return self.argv[1] == "configure"

        if len(self.argv) == 3:
            return self.argv[2] == "--configure"     

        return False  

    def should_show_status(self):
        if len(self.argv) == 2:
            return self.argv[1] == "status"

    def should_deploy(self):
        if len(self.argv) >= 2:
            return self.argv[1] == "deploy"

        return False

    def should_undeploy(self):
        if len(self.argv) >= 2:
            return self.argv[1] == "undeploy"

        return False        

    def clone_repository(self):
        Repository().clone()          

    def say_wellcome(self):
        f = Figlet(font='speed')
        print(colored(f.renderText('dojot'), 'white'))
        print(colored("Welcome to Dojot CLI", 'white', attrs=['bold']))

    def say_thanks(self):
        print("\n\nThanks!\n")

    def say_bye(self):
        print("\n\nBye!\n")      

    def say_k8s_not_installed(self):
        print(constants["k8s_not_installed"])       

    def create_credentials_file(self):
        with open(r'ansible-dojot/credential', 'w') as file:
           file.write(getpass.getpass(prompt="\nSet you password for encrypt vars file: ", stream=None))       

    def create_vars_file_from(self, components):
        if not isinstance(components, list):
            raise ValueError("A list of components is necessary for create vars file")

        for component in components:
            self.vars.update(component.vars)

        with open(r'ansible-dojot/vars.yaml', 'w') as file:
            if any(self.vars):
                yaml.dump(self.vars, file)  
                
        return self        

    def encrypt_vars_file(self):
        self.ansible_cli.encrypt_vars_file()
    
    def run_playbook(self):
        print('\n')
        self.ansible_cli.run_playbook("ansible-dojot/vars.yaml")

    def undeploy(self):
        print('\n')
        self.ansible_cli.undeploy()  

    def show_status(self):
        status = "watch kubectl get pods -n dojot"
        if os.system(status) == 0:
            sys.exit()      
        

        

        