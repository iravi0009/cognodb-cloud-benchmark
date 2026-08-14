from abc import ABC, abstractmethod


class GraphDatabaseAdapter(ABC):
    """
    Common interface for all graph database adapters.
    """

    @abstractmethod
    def connect(self):
        """Connect to the database."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass

    @abstractmethod
    def clear_database(self):
        """Remove benchmark data from the database."""
        pass

    @abstractmethod
    def load_data(self, nodes, relationships):
        """Load benchmark nodes and relationships."""
        pass

    @abstractmethod
    def point_lookup(self, node_id):
        """Execute a point lookup query."""
        pass

    @abstractmethod
    def one_hop_traversal(self, node_id):
        """Execute a 1-hop traversal."""
        pass

    @abstractmethod
    def two_hop_traversal(self, node_id):
        """Execute a 2-hop traversal."""
        pass

    @abstractmethod
    def aggregation(self):
        """Execute an aggregation workload."""
        pass