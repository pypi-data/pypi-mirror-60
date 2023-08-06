import logging
import json
import traceback
import collections
import werkzeug
from flask_logconfig import LogConfig

from flask import g, ctx
# JP: This is loaded into app.config, see extensions.py.   
def log_config(app):

    if app.config.get('LOG_DEBUG_FORMAT',False):
        simple_formatter = 'cc_utils.flask_logging_ext.DebugFormatter'
        audit_formatter =  'cc_utils.flask_logging_ext.DebugFormatter'
    else:
        simple_formatter = 'cc_utils.flask_logging_ext.JsonFormatter'
        audit_formatter =  'cc_utils.flask_logging_ext.JsonAuditFormatter'


    lc = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                '()': simple_formatter
            },
            'audit': {
                '()': audit_formatter
            }
        },
        'filters': {
            'contextual': {
                '()': 'cc_utils.flask_logging_ext.ContextualFilter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'filters': ['contextual'],
                'stream': 'ext://sys.stdout'
            },
            'audit_console': {
                'class': 'logging.StreamHandler',
                'formatter': 'audit',
                'filters': ['contextual'],
                'stream': 'ext://sys.stdout'
            }
        },

        'loggers': {

            'audit_logger': {
                'handlers': ['audit_console'],
                'level': 'INFO'
            },

            'ana_logger': {
                'handlers': ['console'],
                'level': 'INFO'
            },

            app.logger.name: {
                'handlers': ['console'],
                'level': app.config['FLASK_LOG_LEVEL']
            },

        }
    }

    return lc





class ContextualFilter(logging.Filter):
    def filter(self, log_record):
        """ Provide some extra variables to be placed into the log message """

        # If we have an app context (because we're servicing an http request) then get the trace id we have
        # set in g (see app.py)
        if ctx.has_app_context():
            if 'trace_id' in g:
                log_record.trace_id = g.trace_id
            else:
                log_record.trace_id = 'N/A'    
        else:
            log_record.trace_id = 'N/A'
        return True


class DebugFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        if record.msg.__class__ == werkzeug.exceptions.Forbidden:
            desc = record.msg.description
        else:
            desc = str(record.msg)

        l = "%s : %s" % ( self.formatTime(record), desc)

        if record.args:
            l = l + " : %s" % record.args

        if exc:
            l = l + " : %s" % exc

        return l


class JsonFormatter(logging.Formatter):
    def format(self, record):
        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        if record.msg.__class__ == werkzeug.exceptions.Forbidden:
            desc = record.msg.description
        else:
            desc = str(record.msg)

        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', record.levelname),
             ('traceid', record.trace_id),
             ('message', desc),
             ('args', record.args),
             ('exception', exc)])

        return json.dumps(log_entry)


class JsonAuditFormatter(logging.Formatter):
    def format(self, record):

        if record.exc_info:
            exc = traceback.format_exception(*record.exc_info)
        else:
            exc = None

        # Timestamp must be first (webops request)
        log_entry = collections.OrderedDict(
            [('timestamp', self.formatTime(record)),
             ('level', record.levelname),
             ('traceid', record.trace_id),
             ('message', record.msg % record.args),
             ('exception', exc)])

        return json.dumps(log_entry, separators=(',', ':'))



def register_logging(app):
    app.config.update(LOGCONFIG=log_config(app))
    logger = LogConfig()
    app.audit_logger = logging.getLogger("audit_logger")  # for organisational papertrail
    app.ana_logger = logging.getLogger("audit_logger")  # for analytics
    logger.init_app(app)
    app.logger.info("Loggers registered")