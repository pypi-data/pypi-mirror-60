import sys
from . import DojotCLI, Kafka, Gui, Cron, Kong, DeviceManager, Auth, Postgres, MongoDB, Persister, IoTAgentMQTT, IoTAgentLWM2M

class Main:

    def run(self):
        cli = DojotCLI(sys.argv)

        cli.check_requirements()

        if cli.should_show_status():
            cli.show_status()
        
        cli.say_wellcome()

        try:
            if cli.should_configure():
                
                cli.clone_repository()

                kafka = Kafka() \
                    .show_name() \
                    .ask_persistence_time() \
                    .and_if_use_persistent_volume() \
                    .and_volume_size()

                kong = Kong() \
                    .show_name() \
                    .ask_req_per_minute() \
                    .ask_req_per_hour() \
                    .ask_pg_username() \
                    .ask_pg_password()

                devm = DeviceManager() \
                    .show_name() \
                    .ask_pg_username() \
                    .ask_pg_password()

                auth = Auth() \
                    .show_name() \
                    .and_pg_username() \
                    .and_pg_password() \
                    .ask_if_should_send_mail() \
                    .and_smtp_host() \
                    .and_smtp_username() \
                    .and_smtp_password() \
                    .and_password_reset_link()

                postgres = Postgres() \
                    .show_name() \
                    .ask_super_username() \
                    .and_super_password() \
                    .and_if_use_persistent_volume() \
                    .and_volume_size()

                persister = Persister() \
                    .show_name() \
                    .ask_if_messages_will_be_persisted() \
                    .and_persistence_time()

                mongo = MongoDB() \
                    .show_name() \
                    .ask_super_username() \
                    .and_super_password() \
                    .and_if_use_persistent_volume() \
                    .and_volume_size()

                gui = Gui() \
                    .show_name() \
                    .ask_use()

                mqtt = IoTAgentMQTT() \
                    .show_name() \
                    .ask_use() \
                    .and_use_insecure_mqtt()   

                lwm2m = IoTAgentLWM2M() \
                    .show_name() \
                    .ask_use()

                cron = Cron() \
                    .show_name() \
                    .ask_use()

                cli \
                    .create_vars_file_from(
                        [kafka, kong, devm, auth, postgres, persister, mongo, gui, mqtt, lwm2m, cron]
                    )

                cli.create_credentials_file()

                cli.encrypt_vars_file()    
                    

            if cli.should_deploy():
                cli.run_playbook()    

            if cli.should_undeploy():
                cli.undeploy()  

            if cli.should_show_status():
                cli.show_status()      

            cli.say_thanks()

        except KeyboardInterrupt:
            cli.say_bye()
                          