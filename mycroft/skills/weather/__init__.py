from adapt.intent import IntentBuilder
from os.path import dirname
from pyowm.exceptions.api_call_error import APICallError

from mycroft.identity import IdentityManager
from mycroft.skills.core import MycroftSkill
from mycroft.skills.weather.owm_repackaged import OWM
from mycroft.util.log import getLogger

__author__ = 'jdorleans'

LOGGER = getLogger(__name__)


class WeatherSkill(MycroftSkill):
    def __init__(self):
        super(WeatherSkill, self).__init__(name="WeatherSkill")
        self.temperature = self.config['temperature']

    @property
    def owm(self):
        return OWM(API_key=self.config.get('api_key', ''),
                   identity=IdentityManager().get())

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.register_regex("at (?P<Location>.*)")
        self.register_regex("in (?P<Location>.*)")
        self.__build_current_intent()
        self.__build_next_hour_intent()
        self.__build_next_day_intent()

    def __build_current_intent(self):
        intent = IntentBuilder("CurrentWeatherIntent").require(
            "WeatherKeyword").optionally("Location").build()
        self.register_intent(intent, self.handle_current_intent)

    def __build_next_hour_intent(self):
        intent = IntentBuilder("NextHoursWeatherIntent").require(
            "WeatherKeyword").optionally("Location") \
            .require("NextHours").build()
        self.register_intent(intent, self.handle_next_hour_intent)

    def __build_next_day_intent(self):
        intent = IntentBuilder("NextDayWeatherIntent").require(
            "WeatherKeyword").optionally("Location") \
            .require("NextDay").build()
        self.register_intent(intent, self.handle_next_day_intent)

    def handle_current_intent(self, message):
        try:
            location = message.metadata.get("Location", self.location)
            weather = self.owm.weather_at_place(location).get_weather()
            data = self.__build_data_condition(location, weather)
            self.speak_dialog('current.weather', data)
            self.__condition_feedback(weather)
        except APICallError as e:
            self.__api_error(e)
        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    # TODO - Mapping from http://openweathermap.org/weather-conditions
    def __condition_feedback(self, weather):
        status = weather.get_status()
        if status == 'clear':
            self.speak_dialog('sunny.weather')
        elif status == 'rain':
            self.speak_dialog('rain.weather')

    def handle_next_hour_intent(self, message):
        try:
            location = message.metadata.get("Location", self.location)
            weather = self.owm.three_hours_forecast(
                location).get_forecast().get_weathers()[0]
            data = self.__build_data_condition(location, weather)
            self.speak_dialog('hour.weather', data)
        except APICallError as e:
            self.__api_error(e)
        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    def handle_next_day_intent(self, message):
        try:
            location = message.metadata.get("Location", self.location)
            weather = self.owm.daily_forecast(
                location).get_forecast().get_weathers()[1]
            data = self.__build_data_condition(
                location, weather, 'day', 'min', 'max')
            self.speak_dialog('tomorrow.weather', data)
        except APICallError as e:
            self.__api_error(e)
        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    def __build_data_condition(
            self, location, weather, temp='temp', temp_min='temp_min',
            temp_max='temp_max'):
        data = {
            'location': location,
            'scale': self.temperature,
            'condition': weather.get_detailed_status(),
            'temp_current': self.__get_temperature(weather, temp),
            'temp_min': self.__get_temperature(weather, temp_min),
            'temp_max': self.__get_temperature(weather, temp_max)
        }
        return data

    def __get_temperature(self, weather, key):
        return str(int(round(weather.get_temperature(self.temperature)[key])))

    def stop(self):
        pass

    def __api_error(self, e):
        LOGGER.error("Error: {0}".format(e))
        if e._triggering_error.code == 401:
            self.speak_dialog('not.paired')


def create_skill():
    return WeatherSkill()
