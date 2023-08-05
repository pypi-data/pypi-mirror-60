from collections import namedtuple, defaultdict, OrderedDict
from threading import local
from typing import Union, List, Type, Dict

try:
    from django.utils.module_loading import import_module
except ImportError:
    # Django <=1.9.0
    from django.utils.importlib import import_module

from etc.toolbox import get_site_url as get_site_url_, import_app_module, import_project_modules

from .settings import APP_MODULE_NAME, SITE_URL
from .exceptions import UnknownMessageTypeError, UnknownMessengerError

if False:  # pragma: nocover
    from .messages.base import MessageBase
    from .messengers.base import MessengerBase


_MESSENGERS_REGISTRY = OrderedDict()
_MESSAGES_REGISTRY = OrderedDict()

_MESSAGES_FOR_APPS = defaultdict(dict)

_THREAD_LOCAL = local()
_THREAD_SITE_URL = 'sitemessage_site_url'


def get_site_url() -> str:
    """Returns a URL for current site."""

    site_url = getattr(_THREAD_LOCAL, _THREAD_SITE_URL, None)

    if site_url is None:
        site_url = SITE_URL or get_site_url_()
        setattr(_THREAD_LOCAL, _THREAD_SITE_URL, site_url)

    return site_url


def get_message_type_for_app(app_name: str, default_message_type_alias: str)-> Type['MessageBase']:
    """Returns a registered message type object for a given application.

    Supposed to be used by reusable applications authors,
    to get message type objects which may be overridden by project authors
    using `override_message_type_for_app`.

    :param app_name:
    :param default_message_type_alias:

    """
    message_type = default_message_type_alias
    try:
        message_type = _MESSAGES_FOR_APPS[app_name][message_type]
    except KeyError:
        pass
    return get_registered_message_type(message_type)


def override_message_type_for_app(app_name: str, app_message_type_alias: str, new_message_type_alias: str):
    """Overrides a given message type used by a certain application with another one.

    Intended for projects authors, who need to customize messaging behaviour
    of a certain thirdparty app (supporting this feature).
    To be used in conjunction with `get_message_type_for_app`.

    :param app_name:
    :param app_message_type_alias:
    :param new_message_type_alias:

    """
    global _MESSAGES_FOR_APPS

    _MESSAGES_FOR_APPS[app_name][app_message_type_alias] = new_message_type_alias


def register_messenger_objects(*messengers: 'MessengerBase'):
    """Registers (configures) messengers.

    :param messengers: MessengerBase heirs instances.

    """
    global _MESSENGERS_REGISTRY

    for messenger in messengers:
        _MESSENGERS_REGISTRY[messenger.get_alias()] = messenger


def get_registered_messenger_objects() -> Dict[str, 'MessengerBase']:
    """Returns registered (configured) messengers dict
    indexed by messenger aliases.

    """
    return _MESSENGERS_REGISTRY


def get_registered_messenger_object(messenger: str) -> 'MessengerBase':
    """Returns registered (configured) messenger by alias,

    :param messenger: messenger alias

    """
    try:
        return _MESSENGERS_REGISTRY[messenger]

    except KeyError:
        raise UnknownMessengerError('`%s` messenger is not registered' % messenger)


def register_message_types(*message_types: Type['MessageBase']):
    """Registers message types (classes).

    :param message_types: MessageBase heir classes.

    """
    global _MESSAGES_REGISTRY

    for message in message_types:
        _MESSAGES_REGISTRY[message.get_alias()] = message


def get_registered_message_types() -> Dict[str, Type['MessageBase']]:
    """Returns registered message types dict indexed by their aliases."""
    return _MESSAGES_REGISTRY


def get_registered_message_type(message_type: str) -> Type['MessageBase']:
    """Returns registered message type (class) by alias,

    :param message_type: message type alias

    """
    try:
        return _MESSAGES_REGISTRY[message_type]

    except KeyError:
        raise UnknownMessageTypeError('`%s` message class is not registered' % message_type)


def import_app_sitemessage_module(app: str):
    """Returns a submodule of a given app or None.

    :param app: application name

    :rtype: module or None

    """
    return import_app_module(app, APP_MODULE_NAME)


def import_project_sitemessage_modules():
    """Imports sitemessages modules from registered apps."""
    return import_project_modules(APP_MODULE_NAME)


def is_iterable(v):
    """Tells whether the thing is an iterable.
    NB: strings do not count even on Py3.

    """
    return hasattr(v, '__iter__') and not isinstance(v, str)


# Class used to represent message recipients.
Recipient = namedtuple('Recipient', ('messenger', 'user', 'address'))


def recipients(messenger: Union[str, 'MessengerBase'], addresses: Union[List[str], str]) -> List[Recipient]:
    """Structures recipients data.

    Returns Recipient objects.

    :param messenger: MessengerBase heir

    :param addresses: recipients addresses or Django User
        model heir instances (NOTE: if supported by a messenger)

    """
    if isinstance(messenger, str):
        messenger = get_registered_messenger_object(messenger)

    return messenger.structure_recipients_data(addresses)
