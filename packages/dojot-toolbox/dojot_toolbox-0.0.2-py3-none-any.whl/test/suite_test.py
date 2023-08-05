import unittest
from . import * 

def suite():
    suite = unittest.TestSuite()
    suite.addTest(IoTAgentMoscaTest())
    suite.addTest(IoTAgentLWM2MTest())
    suite.addTest(PostgresTest())
    suite.addTest(AuthTest())
    suite.addTest(AuthenticableTest())
    suite.addTest(CronTest())
    suite.addTest(GuiTest())
    suite.addTest(InstallerTest())
    suite.addTest(KafkaTest())
    suite.addTest(KongTest())
    suite.addTest(MongoDBTest())
    suite.addTest(OptionalTest())
    suite.addTest(PersistentTest())
    suite.addTest(RepositoryTest())
    suite.addTest(ScalableTest())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())