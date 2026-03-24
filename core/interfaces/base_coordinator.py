from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class NetworkCoordinator(ABC):
    """
    Abstract base class for communicating with arbitrary distributed computing managers
    or databases (Firebase, SQLite, Kafka, etc.) to negotiate work payloads.
    
    Implementations must be problem-agnostic. The problem_name is passed at construction
    to namespace all database paths automatically.
    """
    @abstractmethod
    def fetch_work_unit(self) -> Optional[Dict]:
        """
        Retrieves a bounding phase-space block to process from the distributed queue.
        
        Returns:
            A dictionary containing the bounds payload, or None if the search space is exhausted.
        """
        pass

    @abstractmethod
    def submit_results(self, verified_discoveries: List[Dict]) -> bool:
        """
        Transmits verified discoveries to the centralized persistence layer.
        
        Returns:
            True if successful. On False, the framework triggers local caching overrides.
        """
        pass
    
    def report_telemetry(self, combinations_evaluated: int, gpu_seconds: float):
        """
        Report compute telemetry after a work unit completes.
        Implementations should atomically increment node-level and problem-level counters.
        
        Default implementation is a no-op for coordinators that don't support telemetry.
        """
        pass
