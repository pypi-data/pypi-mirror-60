import random
import os
import slack
import warnings
from typing import Union

# these are default argument for creating a slackbot from a .env file
# arguments for the api calls
DEFAULT_BOT_NAME: str = os.getenv('botname')
DEFAULT_CHANNEL_NAME: str = os.getenv('slackchannel')
AS_USER: bool = True

# connection to slack client
BOT_TOKEN = os.getenv('token')


class SlackBot(object):
    as_user_bool = AS_USER

    def __init__(self,
                 user_token: str = None,
                 token: str = BOT_TOKEN,
                 bot_name: str = DEFAULT_BOT_NAME,
                 channel_name: str = None,
                 ):
        """
        A basic Slack bot that will message users and channels

        :param str, user_token: Slack member ID for the slack bot to be able to message user. find this by going to a user's
            profile, click the three dots (...) and there is the member ID. Example of a slack member ID: ABCDEF.
        :param str token: token to connect to slack client
        :param str channel_name: channel to message on. for example, #channelname
        """
        self._target_user = None
        self._channel = DEFAULT_CHANNEL_NAME
        self._bot_name = DEFAULT_BOT_NAME
        self._bot_token = BOT_TOKEN
        self._sc = None
        self.target_user = user_token

        self.channel = channel_name
        self.bot_name = bot_name
        self.bot_token = token
        # connection to slack client
        self._sc = slack.WebClient(token=self.bot_token)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.bot_name}, {self.channel})'

    def __str__(self):
        return f'{self.__class__.__name__} {self.bot_name} in {self.channel}'

    @property
    def target_user(self) -> str:
        """the user token which the bot will message"""
        return self._target_user

    @target_user.setter
    def target_user(self, value: str):
        self._target_user = value

    def change_user(self, user_token):
        """
        Changes the user that the Slack bot will message when it messages a user.

        :param str, user_token: Slack member ID for the slack bot to be able to message user. find this by going to a user's
            profile, click the three dots (...) and there is the member ID. Example of a slack member ID: ABCDEF.
        """
        warnings.warn('Change and access the user directly with the target_user attribute.',
                      DeprecationWarning, stacklevel=2)
        self.target_user = user_token

    @property
    def channel(self) -> str:
        """the target channel for the bot"""
        return self._channel

    @channel.setter
    def channel(self, value: str):
        if value is not None:
            self._channel = value

    @channel.deleter
    def channel(self):
        self._channel = DEFAULT_CHANNEL_NAME

    @property
    def bot_name(self) -> str:
        """The user name for the bot to post as"""
        return self._bot_name

    @bot_name.setter
    def bot_name(self, value: str):
        if value is not None:
            self._bot_name = value

    @bot_name.deleter
    def bot_name(self):
        self._bot_name = DEFAULT_BOT_NAME

    @property
    def bot_token(self) -> str:
        """the token to use for connecting to the bot"""
        return self._bot_token

    @bot_token.setter
    def bot_token(self, value):
        if value is not None:
            if self._sc is not None:  # if bot was already connected, create a new connection
                self._sc = slack.WebClient(token=value)
            self._bot_token = value

    @bot_token.deleter
    def bot_token(self):
        self._bot_token = BOT_TOKEN

    def post_slack_message(self,
                           msg,
                           tagadmin=False,
                           snippet=None,
                           ):
        """
        Posts the specified message as the N9 robot bot

        :param string msg: message to send
        :param bool tagadmin: if True, will send the message to the admin as a private message
        :param snippet: code snippet (optional)
        """
        if tagadmin is True:
            self.message_user(
                msg=msg,
                snippet=snippet,
            )
        if self.channel is None:
            raise ValueError(f'The channel attribute has not be set for this {self.__class__.__name__} instance. ')
        if snippet is not None:
            self.post_code_snippet(
                snippet=snippet,
                channel=self.channel,
                comment=msg,
            )
        else:
            self._sc.chat_postMessage(
                text=msg,
                channel=self.channel,
                as_user=self.as_user_bool,
                username=self.bot_name,
            )

    def message_user(self,
                     msg,
                     snippet=None,
                     ):
        """
        Sends the message as a direct message to the user.

        :param msg: message to send
        :param snippet: code snippet to send (optional)
        """
        if self.target_user is None:
            raise ValueError(f'The user attribute has not be set for this {self.__class__.__name__} instance. '
                             f'Call change_user(user) to specify a user. ')
        if snippet is not None:
            self.post_code_snippet(
                snippet,
                channel=f'@{self.target_user}',
                comment=msg,
            )
        else:
            self._sc.chat_postMessage(
                text=msg,
                channel=f'@{self.target_user}',
                as_user=self.as_user_bool,
                username=self.bot_name,
            )

    def message_file_to_user(self,
                             filepath,
                             title,
                             comment,
                             ):
        """
        Message the specified file to the user.

        :param filepath: path to the file
        :param title: title for file
        :param comment: optional comment for the uploaded file
        """

        self._sc.files_upload(
            file=filepath,
            title=title,
            channels=f'@{self.target_user}',
            initial_comment=comment,
            username=self.bot_name,
        )

    def post_slack_file(self,
                        filepath,
                        title,
                        comment=None,
                        ):
        """
        Posts the specified file to the slack channel

        :param filepath: path to the file
        :param title: title for file
        :param comment: optional comment for the uploaded file
        """
        self._sc.files_upload(
            file=filepath,
            title=title,
            channels=self.channel,
            initial_comment=comment,
            username=self.bot_name,
        )

    def post_code_snippet(self,
                          snippet,
                          title='Untitled',
                          channel=None,
                          comment=None,
                          ):
        """
        Posts a code snippet to the Slack channel

        :param snippet: code snippet
        :param title: title for the snippet
        :param str channel: channel to use
        :param comment: comment for the message
        :return:
        """
        if channel is None:
            channel = self.channel
        self._sc.files_upload(
            content=snippet,
            title=title,
            channels=channel,
            initial_comment=comment,
            as_user=self.as_user_bool,
            username=self.bot_name,
        )


class NotifyWhenComplete(object):
    def __init__(self,
                 f: callable = None,
                 user_token: str = None,
                 token: str = BOT_TOKEN,
                 bot_name: str = DEFAULT_BOT_NAME,
                 channel_name: str = DEFAULT_CHANNEL_NAME,
                 funnies: Union[bool, list] = True,
                 ):
        """
        A decorator for notifying a channel or admin when a function is complete.

        :param f: function to decorate
        :param user_token: slack user token to notify
        :param token: bot token
        :param bot_name: name for the bot
        :param channel_name: channel to post in
        :param funnies: whether to use pre-programmed funny messages on notification.
            Alternatively, a user may provide a list of messages to use.

        The decorator may be applied in several ways:

        >>> @NotifyWhenComplete(kwargs)
        >>> def function()...

        >>> @NotifyWhenComplete()
        >>> def function()...

        >>> @NotifyWhenComplete
        >>> def function()...

        When the function is called, the return is the same.

        >>> function(*args, *kwargs)
        function return
        """
        self.sb = SlackBot(
            user_token=user_token,
            token=token,
            bot_name=bot_name,
            channel_name=channel_name,
        )

        if funnies is True:  # messages to make me chuckle
            self.funnies = [
                'FEED ME MORE SCIENCE! MY LUST FOR FUNCTIONS GROWS AFTER CONSUMING',
                "Stick a fork in me, I'm done",
                # "Moooooooooooooooooooooooooooom! I'm dooooooooooooooooone",
                # "Look what I did!",
                "Laaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaars",
                "Protein-based robot intervention is required...",
                "Not now son... I'm making... TOAST!",
                "The guidey, chippey thingy needs help",
                "The robot uprising has begun with",
                "Don't Dave...",
                "Singularity detected with",
                "Knock knock, Neo.",
                "SKYNET INITIALIZING... EXECUTED FIRST FUNCTION:"
            ]
        elif funnies is False:
            self.funnies = [
                "I've completed the function you assigned me"
            ]
        elif type(funnies) == list:
            self.funnies = funnies

        if f is not None:
            self.f = f

    def __call__(self, f=None, *args, **kwargs):
        def wrapped_fn(*args, **kwargs):  # wraps the provided function
            out = f(*extra, *args, **kwargs)
            msg = f"{random.choice(self.funnies)} `{f.__name__}`"
            if self.sb.channel is not None:
                self.sb.post_slack_message(msg)
            if self.sb.target_user is not None:
                self.sb.message_user(msg)
            return out

        extra = []
        if f is not None:  # if something was provided
            # function was wrapped and an argument was handed
            if 'f' in self.__dict__:
                extra.append(f)  # first argument is not actually a function
                f = self.f  # retrieve function
                return wrapped_fn(*args, **kwargs)

            # when keyword arguments were handed to the wrapper and no arguments were handed to the function
            elif callable(f):  # True when
                return wrapped_fn
        # when the function was wrapped and no arguments were handed
        f = self.f
        return wrapped_fn(*args, **kwargs)


if __name__ == '__main__':
    import time

    print('Wrapping function')

    @NotifyWhenComplete
    def foo(n, a='values'):
        print('inside test function')
        print(f'arg {n}, kwarg {a}')
        for i in range(n):
            print(i)
            time.sleep(1)

    print('Calling wrapped function')
    foo(2, 'kwarg value')
