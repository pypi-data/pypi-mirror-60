from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import functools

from trend_app_protect.exceptions import (
    TrendAppProtectBlocked,
    TrendAppProtectOverrideResponse,
)
from trend_app_protect.singleton import get_agent


def protect_handler(handler):
    """
    Decorator to protect an AWS Lambda function handler.
    Use on your handler function:

        @protect_handler
        def handler(event, context):
            ...
    """
    agent = get_agent()

    @functools.wraps(handler)
    def wrapper(event, context):
        # If agent is disabled, call through to original
        if not agent.enabled:
            return handler(event, context)

        transaction = agent.start_transaction()
        try:
            agent.run_hook(__name__, "lambda_function_start",
                           {
                               "event": event,
                               "context": {
                                   "function_name": context.function_name,
                                   "function_version":
                                       context.function_version,
                                   "aws_request_id": context.aws_request_id,
                                   "invoked_function_arn":
                                       context.invoked_function_arn,
                               }
                           },
                           transaction=transaction)
            try:
                return handler(event, context)
            # Since TrendAppProtectOverrideResponse derives from BaseException,
            # the Python runtime does not catch it - if we let it bubble up,
            # the lambda does not produce a response, and the client times out.
            # So re-raise as an exception derived from Exception.
            except TrendAppProtectOverrideResponse as exc:
                raise TrendAppProtectBlocked(*exc.args)
        finally:
            agent.finish_transaction(transaction)

    return wrapper
