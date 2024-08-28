from abc import ABC, abstractmethod


class Migration(ABC):
    def __init__(self, conn):
        self.conn = conn

    """
    Abstract class for database migrations.

    Each migration should implement the up and down methods to apply and revert changes.
    """

    @abstractmethod
    async def up(self):
        """
        Apply the migration.
        This method needs to be implemented in each concrete migration class.
        """
        pass

    @abstractmethod
    async def down(self):
        """
        Revert the migration.
        This method needs to be implemented in each concrete migration class.
        """
        pass
