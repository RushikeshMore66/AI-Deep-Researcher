from core.models import ResearchState
from utils.logger import get_logger

logger = get_logger("Core.StateManager")

class StateManager:
    def __init__(self, initial_query: str):
        self._state = ResearchState(input_query=initial_query)
        logger.info(f"Initialized StateManager for query: {initial_query}")

    @property
    def state(self) -> ResearchState:
        return self._state

    def update(self, **kwargs):
        """Updates the state with new values."""
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)
                logger.debug(f"Updated state field '{key}'")
            else:
                logger.warning(f"Tried to update non-existent state field: {key}")

    def add_error(self, error_msg: str):
        """Adds an error message to the state."""
        self._state.errors.append(error_msg)
        logger.error(f"State Error Added: {error_msg}")

    def get_summary(self) -> str:
        """Returns a summary of the current state."""
        return (
            f"Query: {self._state.input_query} | "
            f"Intent: {self._state.intent.kind if self._state.intent else 'None'} | "
            f"Angles: {len(self._state.angles)} | "
            f"Sources: {sum(len(v) for v in self._state.sources_by_angle.values())} | "
            f"Claims: {len(self._state.all_claims)}"
        )
