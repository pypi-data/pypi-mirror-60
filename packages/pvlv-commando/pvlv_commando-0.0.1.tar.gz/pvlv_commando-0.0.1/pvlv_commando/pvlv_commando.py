import os
from pvlv_commando.commando.command_importer import (
    importer,
    build_descriptor,
)
from pvlv_commando.commando.command_descriptor import CommandDescriptor
from pvlv_commando.commando.command_structure_reader import read_command_structure
from pvlv_commando.manual.manual import Manual
from pvlv_commando.exceptions.permissions_exceptions import InsufficientPermissions
from pvlv_commando.exceptions.errors_exceptions import (
    CommandNotFound,
    ManualExecutionFail,
    CommandExecutionFail,
)
from pvlv_commando.configurations.configuration import logger


class Commando(object):
    """
    Commando class to handle commands in a easy way
    The exception handling must be done outside of this class
    """
    def __init__(self):
        """
        Load all the packages and commands should be done only once.
        For efficiency it must be put as a static class for all the project.
        """
        self.__command_list = importer()
        """
        Structure of the command found
        Stored to be executed
        """
        self.__command_found = None
        self.language = 'eng'
        self.trigger = None
        self.arg = None
        self.params = {}

        self.__permissions = 0

        # Do not append built in commands
        # Builtin manual
        self.__is_manual = False

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.__manual = build_descriptor('builtin', 'manual', dir_path + '/manual/manual.json')

        self.__command_descriptors = []
        for cd in self.__command_list:
            self.__command_descriptors.append(cd[0])

        logger.info('Commando Loaded')

    def __check_command_integrity(self):
        """
        Check if the command has an allowed arg and params
        Do input validation of the arg and params
        """
        # command_descriptor, module, class_name = self.__command_found

        if not self.params.keys() in self.__manual.handled_params_list():
            pass

    def find_command(self, text: str, language: str, permissions: int):
        """
        Find if there is a command in the text
        N.B.: YOU HAVE TO REMOVE THE COMMAND CHAR/STR TRIGGER AND SEND CLEAN TEXT

        :param text: the message without the chat/str command invocation
        :param language: the language code for message response
        :param permissions: the user permission in the guild/chat
        :return: True if there is a command else False
        """
        self.language = language
        self.__permissions = permissions

        self.trigger, self.arg, self.params = read_command_structure(text)

        # Check build in commands
        if self.trigger in self.__manual.invocation_words:
            self.__is_manual = True
            return

        # Check custom commands
        for command in self.__command_list:
            command_descriptor, module, class_name = command
            if self.trigger in command_descriptor.invocation_words:
                self.__command_found = command
                return

        raise CommandNotFound(self.language, self)

    @property
    def command(self):
        """
        Get the command item object to access to all the information of the command
        :return: command_descriptor
        """
        command_descriptor: CommandDescriptor
        command_descriptor, module, class_name = self.__command_found
        return command_descriptor

    def run_command(self, bot):
        """
        Execute the command
        :param bot: the bot var, that will be passed to the command. Used to send message and perform actions.
        If you have multiple params to pass to the command use a tuple inside the bot or a dict
        """
        if self.__is_manual:
            return

        command_descriptor, module, class_name = self.__command_found

        if command_descriptor.permissions >= self.__permissions:
            raise InsufficientPermissions(self.language)
        self.__permissions = 0  # Reset permissions

        logger.info('RUN: ' + command_descriptor.name)

        command_class = getattr(module, class_name)

        try:
            command = command_class(bot, self.language, command_descriptor, self.arg, self.params)
            command.run()
        except Exception as exc:
            logger.error(exc)
            raise CommandExecutionFail(
                self.language,
                full_exception=exc,
                command=command_descriptor,
                arg=self.arg,
                params=self.params
            )

    def run_manual(self, max_chunk_len=1500):
        """
        The manual is cut in chunks and return the chunks array
        This is made because some chats have a limit in message len

        :param max_chunk_len: the max len of the text
        :return: an array of strings, where each string has the max len of the max_chunk_len
        """
        if not self.__is_manual:
            return
        self.__is_manual = False

        logger.info('RUN: manual')

        try:
            manual = Manual(
                self.language,
                self.__manual,
                self.__command_descriptors,
                self.arg,
                self.params,
                max_chunk_len,
                self.__permissions
            )
            self.__permissions = 0  # Reset permissions
            return manual.run()
        except Exception as exc:
            logger.error(exc)
            raise ManualExecutionFail(self.language, self, full_exception=exc)
