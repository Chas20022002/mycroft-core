import feedparser
import time
from os.path import dirname

import mycroft.skills.weather as weather
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util import play_mp3
from mycroft.util.log import getLogger

__author__ = 'jdorleans'

LOGGER = getLogger(__name__)


class NPRNewsSkill(MycroftSkill):
    def __init__(self):
        super(NPRNewsSkill, self).__init__(name="NPRNewsSkill")
        self.url_rss = self.config['url_rss']
        self.weather = weather.WeatherSkill()
        self.process = None

    def initialize(self):
        self.load_data_files(dirname(__file__))
        intent = IntentBuilder("NPRNewsIntent").require(
            "NPRNewsKeyword").build()
        self.register_intent(intent, self.handle_intent)

        self.weather.bind(self.emitter)
        self.weather.load_data_files(dirname(weather.__file__))

    def handle_intent(self, message):
        try:
            data = feedparser.parse(self.url_rss)
            self.speak_dialog('npr.news')
            time.sleep(3)
            self.process = play_mp3(data['entries'][0]['links'][0]['href'])

        except Exception as e:
            LOGGER.error("Error: {0}".format(e))

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait()


def create_skill():
    return NPRNewsSkill()
