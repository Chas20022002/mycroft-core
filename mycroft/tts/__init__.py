import abc
from os.path import dirname, exists, isdir

from mycroft.util.log import getLogger

__author__ = 'jdorleans'

LOGGER = getLogger(__name__)


class TTS(object):
    """
    TTS abstract class to be implemented by all TTS engines.

    It aggregates the minimum required parameters and exposes
    ``execute(sentence)`` function.
    """

    def __init__(self, lang, voice, filename='/tmp/tts.wav'):
        super(TTS, self).__init__()
        self.lang = lang
        self.voice = voice
        self.filename = filename

    @abc.abstractmethod
    def execute(self, sentence):
        pass


class TTSValidator(object):
    """
    TTS Validator abstract class to be implemented by all TTS engines.

    It exposes and implements ``validate(tts)`` function as a template to
    validate the TTS engines.
    """

    def __init__(self):
        pass

    def validate(self, tts):
        self.__validate_instance(tts)
        self.__validate_filename(tts.filename)
        self.validate_lang(tts.lang)
        self.validate_connection(tts)

    def __validate_instance(self, tts):
        instance = self.get_instance()
        if not isinstance(tts, instance):
            raise AttributeError(
                'tts must be instance of ' + instance.__name__)
        LOGGER.debug('TTS: ' + str(instance))

    def __validate_filename(self, filename):
        if not (filename and filename.endswith('.wav')):
            raise AttributeError(
                'filename: ' + filename + ' must be a .wav file!')
        dir_path = dirname(filename)

        if not (exists(dir_path) and isdir(dir_path)):
            raise AttributeError(
                'filename: ' + filename + ' is not a valid file path!')
        LOGGER.debug('Filename: ' + filename)

    @abc.abstractmethod
    def validate_lang(self, lang):
        pass

    @abc.abstractmethod
    def validate_connection(self, tts):
        pass

    @abc.abstractmethod
    def get_instance(self):
        pass
