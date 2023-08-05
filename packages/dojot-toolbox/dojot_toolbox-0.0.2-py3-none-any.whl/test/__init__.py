from .iotagent_mqtt_test import IoTAgentMoscaTest
from .iotagent_lwm2m_test import IoTAgentLWM2MTest
from .postgres_test import PostgresTest
from .auth_test import AuthTest
from .authenticable_test import AuthenticableTest
from .cron_test import CronTest
from .gui_test import GuiTest
# from .installer_test import InstallerTest
from .kafka_test import KafkaTest
from .kong_test import KongTest
from .mongodb_test import MongoDBTest
from .persister_test import PersisterTest
from .optional_test import OptionalTest
from .persistent_test import PersistentTest
from .repository_test import RepositoryTest
from .scalable_test import ScalableTest

# python3 -m unittest test.installer_test