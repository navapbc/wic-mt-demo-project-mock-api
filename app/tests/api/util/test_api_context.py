import pytest

from api.util.api_context import api_context_manager


def test_get_api_context_no_current_request(app):
    # You can't get the DB session from the App if there
    # isn't a request ("g.db" gets set in a handler before the request starts)
    with app.app.app_context():
        # The app exists inside this block, but no request has started
        with pytest.raises(Exception, match="No database session available in application context"):
            with api_context_manager():
                # Need to call it like this so it actually fails
                pass


def test_get_api_context_no_current_app(app):
    # You can't get an API context if the app isn't running
    with pytest.raises(RuntimeError, match="Working outside of application context."):
        with api_context_manager():
            # Need to call it like this so it actually fails
            pass
