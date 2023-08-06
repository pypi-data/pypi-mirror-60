import logging
import os
from multiprocessing import Process

import rasa.cli.utils
import ragex.community.jwt
import ragex.community.metrics
import ragex.community.utils as rage_x_utils
from ragex.community import config, metrics


logger = logging.getLogger(__name__)

def main():
    pass


def _event_service() -> None:
    # Update metrics config for this new process
    logger.debug("Temp stop event service")
    # from rasax.community.services.event_service import main as event_service_main
    #
    # event_service_main(should_run_liveness_endpoint=False)

def launch_event_service() -> None:
    """Start the event service in a multiprocessing.Process if
        `EVENT_CONSUMER_SEPARATION_ENV` is `True`, otherwise do nothing."""

    from ragex.community.constants import EVENT_CONSUMER_SEPARATION_ENV


    if config.should_run_event_consumer_separately:
        logger.debug(
            f"Environment variable '{EVENT_CONSUMER_SEPARATION_ENV}' "
            f"set to 'True', meaning Rasa X expects the event consumer "
            f"to run as a separate service."
        )
    else:
        logger.debug("Starting event service from Rage X")
        p = Process(target=_event_service)
        p.daemon = True
        p.start()


if __name__ == "__main__":
    rage_x_utils.update_log_level()

    launch_event_service()

    logger.debug("Starting API Service")
    main()

