from logging import Handler

from opsas.utils.HttpSession import HttpSession


class SlackMessager(HttpSession):

    def __init__(self, logger, token, channel):
        super().__init__(logger, endpoint='https://slack.com/api')
        self.session.headers.setdefault('Authorization', 'Bearer ' + token)
        self.session.headers.setdefault('Content-Type', 'application/json')
        self.channel = channel

    def post_payload(self, payload):
        response = self.request_conn(method='post', path='/chat.postMessage', data=payload).json()
        self.logger.info(response)
        return response

    def send_text_message(self, message):
        payload = {
            'channel': self.channel,
            'text': message,
            'type': 'text'
        }
        return self.post_payload(payload)

    def send_message(self, message, infolevel="debug", thread_ts=None):
        payload = self.make_payload(message, infolevel, thread_ts=thread_ts)
        return self.post_payload(payload)

    def create_thread(self, name):
        response = self.send_text_message(name)
        return response['ts']

    def make_payload(self, message, loglevel, thread_ts=None):
        self.logger.debug(loglevel)
        payload = {
            'channel': self.channel,
            'blocks': [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "image",
                            "image_url": f"http://img.justcalm.ink/{loglevel}.png",
                            "alt_text": f"{loglevel} icon"
                        },
                        {
                            "type": "mrkdwn",
                            "text": message
                        }
                    ]
                }
            ]
        }
        if thread_ts is not None:
            payload['thread_ts'] = thread_ts
        return payload


class SlackLogHandler(Handler):
    """SlackLogHandler for python logging.logger object

    Parameters
    -----------
    token: str
        slack app oauth token
    channel: str
        slack channel name
    logger: logging.logger,optional
        logger object for logging logs when slackloghandler,

    Note
    --------
    This slacklog handler used slack app to sendmessage.

    Create a slack app and follower guides to allow it to connect and chat in channel https://api.slack.com/apps?new_app=1.

    Examples
    ---------

    >>> import logging
    >>> logger = logging.getLogger('slack')
    >>> logging.basicConfig()
    >>> slackLogHandler = SlackLogHandler(channel='test',token='xxx')
    >>> logger.addHandler(slackLogHandler)
    >>> logger.info("info")
    >>> logger.warning("warnning")

    >>> import logging
    >>> logging.basicConfig()
    >>> logger = logging.getLogger("slack")
    >>> slackLogHandler = SlackLogHandler(channel='test',token='xxx')
    >>> slackLogHandler.create_session('testDialog')
    >>> logger.addHandler(slackLogHandler)
    >>> logger.warning('warining')

    """

    _thread_ts_list = {}

    def __init__(self, token, channel, logger=None):
        super().__init__()
        self.bot = SlackMessager(token=token, channel=channel, logger=logger)

    def create_session(self, name):
        """
        By default,logs were send to slack channel directly.
        Can also start a dialog in slack channel and all logs send as reply to this message
        Parameters
        ----------
        name: str
          dialog name

        Return
        ---------
        None
        """
        self._thread_ts_list[name] = self.bot.create_thread(name)

    def emit(self, record):
        msg = self.format(record)
        thread_name = record.name
        thread_ts = self._thread_ts_list.get(thread_name, None)
        return self.bot.send_message(message=msg, infolevel=record.levelname.lower(), thread_ts=thread_ts)
