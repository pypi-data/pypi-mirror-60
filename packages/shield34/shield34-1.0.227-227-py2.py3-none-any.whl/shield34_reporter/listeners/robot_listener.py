from shield34_reporter.auth.sdk_authentication import SdkAuthentication
from shield34_reporter.exceptions import Shield34PropertiesFileNotFoundException, \
    Shield34PropertiesSyntaxIncorrect, Shield34LoginFailedException
from shield34_reporter.utils.logger import Shield34Logger
from .shield34_listener import Shield34Listener
from shield34_reporter.overrider.selenium_overrider import SeleniumOverrider
import robot


class RobotListener(object):

    ROBOT_LISTENER_API_VERSION = 3

    shield34_listener = Shield34Listener()

    def __init__(self, ini_file_path=''):
        from shield34_reporter.consts.shield34_properties import Shield34Properties
        self.ROBOT_LIBRARY_LISTENER = self
        Shield34Logger.set_logger(robot.api.logger)
        try:
            if ini_file_path != '':
                Shield34Properties.propertiesFilePath = ini_file_path
            Shield34Logger.logger.console("Searching for configuration ini file...")
            SdkAuthentication.login()
            Shield34Logger.logger.console("Logged in successfully to Shield34")

        except Shield34PropertiesFileNotFoundException as e:
            Shield34Logger.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Logger.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Logger.logger.warn(e)

    def start_suite(self, data, result):
        try:
            SeleniumOverrider.override()
            self.shield34_listener.on_suite_start(suite_name=data.name)
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Logger.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Logger.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Logger.logger.warn(e)

    def end_suite(self, data, result):
        pass

    def start_test(self, test, result):
        try:
            self.shield34_listener.on_test_start(test_name=test.name, test_class_name=test.longname)
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Logger.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Logger.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Logger.logger.warn(e)

    def end_test(self, data, result):
        try:
            if result.status == 'PASS':
                self.shield34_listener.on_test_success()
                self.shield34_listener.on_test_finish()

            elif result.status == 'FAIL':
                self.shield34_listener.on_test_failure(result)
                self.shield34_listener.on_test_finish()

            elif result.status == 'SKIPPED':
                self.shield34_listener.on_test_skipped()
                self.shield34_listener.on_test_finish()
        except Shield34PropertiesFileNotFoundException as e:
            Shield34Logger.logger.warn(e)
        except Shield34PropertiesSyntaxIncorrect as e:
            Shield34Logger.logger.warn(e)
        except Shield34LoginFailedException as e:
            Shield34Logger.logger.warn(e)


