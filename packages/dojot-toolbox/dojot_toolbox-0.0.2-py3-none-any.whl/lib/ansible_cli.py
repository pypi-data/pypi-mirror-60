import json
import shutil
import os
from progress.bar import Bar
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.vault import VaultLib
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.playbook import Playbook
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.module_utils._text import to_bytes
from ansible.parsing.vault import VaultSecret
from ansible import context
import ansible.constants as C


#TODO: Realizar testes na classe inteira
class ResultCallback(CallbackBase):

    def __init__(self, bar):
        self.bar = bar

   
    def v2_runner_on_ok(self, result, **kwargs):
        self.bar.next()
        # host = result._host
        # print(json.dumps({host.name: result._result}, indent=4))


class AnsibleCLI:

    def encrypt_vars_file(self):
        vault = "ansible-vault encrypt --vault-id ./ansible-dojot/credential ansible-dojot/vars.yaml"
        os.system(vault) == 0 

    def undeploy(self):
        context.CLIARGS = ImmutableDict(connection='local', module_path=None, forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False)   
        
        loader = DataLoader()
        passwords = dict(vault_pass='123')

        inventory = InventoryManager(loader=loader, sources=('ansible-dojot/inventories/example_local',))

        variable_manager = VariableManager(loader=loader, inventory=inventory)

        playbook = Playbook.load('ansible-dojot/undeploy.yaml', variable_manager=variable_manager, loader=loader)  

        with Bar('Undeploying', max=2) as bar:
            tqm = None
            results_callback = ResultCallback(bar)

            try:
                for play in playbook.get_plays():
                    tqm = TaskQueueManager(
                            inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader,
                            passwords=passwords,
                            stdout_callback=results_callback,
                        )
                    tqm.run(play)
            finally:
                bar.finish
                if tqm is not None:
                    tqm.cleanup()                      

    
    def run_playbook(self, vars_file):
        context.CLIARGS = ImmutableDict(connection='local', module_path=None, forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False, extra_vars={"@{}".format(vars_file)})

        loader = DataLoader()
        loader.set_vault_secrets([('default', VaultSecret(_bytes=to_bytes('123')))])
        passwords = dict(vault_pass='123')

        inventory = InventoryManager(loader=loader, sources=('ansible-dojot/inventories/example_local',))

        variable_manager = VariableManager(loader=loader, inventory=inventory)

        playbook = Playbook.load('ansible-dojot/deploy.yaml', variable_manager=variable_manager, loader=loader)

        with Bar('Deploying', max=36) as bar:
            tqm = None
            results_callback = ResultCallback(bar)

            try:
                for play in playbook.get_plays():
                    tqm = TaskQueueManager(
                            inventory=inventory,
                            variable_manager=variable_manager,
                            loader=loader,
                            passwords=passwords,
                            stdout_callback=results_callback,
                        )
                    tqm.run(play)
            finally:
                bar.finish
                if tqm is not None:
                    tqm.cleanup()                        
