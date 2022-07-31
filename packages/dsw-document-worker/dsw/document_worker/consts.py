DEFAULT_ENCODING = 'utf-8'
EXIT_SUCCESS = 0
VERSION = '3.14.0rc1'
PROG_NAME = 'docworker'
LOGGER_NAME = 'docworker'
CURRENT_METAMODEL = 9
NULL_UUID = '00000000-0000-0000-0000-000000000000'


class DocumentState:
    QUEUED = 'QueuedDocumentState'
    PROCESSING = 'InProgressDocumentState'
    FAILED = 'ErrorDocumentState'
    FINISHED = 'DoneDocumentState'


class TemplateAssetField:
    UUID = 'uuid'
    FILENAME = 'fileName'
    CONTENT_TYPE = 'contentType'


class FormatField:
    UUID = 'uuid'
    NAME = 'name'
    STEPS = 'steps'


class StepField:
    NAME = 'name'
    OPTIONS = 'options'


class DocumentNamingStrategy:
    UUID = 'uuid'
    SANITIZE = 'sanitize'
    SLUGIFY = 'slugify'

    _DEFAULT = SANITIZE
    _NAMES = {
        'uuid': UUID,
        'sanitize': SANITIZE,
        'slugify': SLUGIFY,
    }

    @classmethod
    def get(cls, name: str):
        return cls._NAMES.get(name.lower(), cls._DEFAULT)


CMD_CHANNEL = 'doc_worker'
CMD_COMPONENT = 'doc_worker'


class CommandState:
    NEW = 'NewPersistentCommandState'
    DONE = 'DonePersistentCommandState'
    ERROR = 'ErrorPersistentCommandState'
    IGNORE = 'IgnorePersistentCommandState'


class Queries:

    LISTEN = f'LISTEN persistent_command_channel__{CMD_CHANNEL};'

    # TODO: configurable exp wait on retry?
    SELECT_CMD = f"""
        SELECT *
        FROM persistent_command
        WHERE component = '{CMD_COMPONENT}'
          AND attempts < max_attempts
          AND state != '{CommandState.DONE}'
          AND state != '{CommandState.IGNORE}'
          AND updated_at < (%(now)s - (2 ^ attempts - 1) * INTERVAL '1 min')
        ORDER BY attempts ASC, updated_at DESC
        LIMIT 1 FOR UPDATE SKIP LOCKED;
    """

    UPDATE_CMD_ERROR = f"""
        UPDATE persistent_command
        SET attempts = %(attempts)s,
            last_error_message = %(error_message)s,
            state = '{CommandState.ERROR}',
            updated_at = %(updated_at)s
        WHERE uuid = %(uuid)s;
    """

    UPDATE_CMD_DONE = f"""
        UPDATE persistent_command
        SET attempts = %(attempts)s,
            state = '{CommandState.DONE}',
            updated_at = %(updated_at)s
        WHERE uuid = %(uuid)s;
    """

    SELECT_APP_CONFIG = """
        SELECT *
        FROM app_config
        WHERE uuid = %(app_uuid)s;
    """
