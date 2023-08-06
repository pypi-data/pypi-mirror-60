""" Holds objects for interacting with Redis connections """

import redis

import dbreak.connections
import dbreak.parser


class RedisWrapper(dbreak.connections.ConnectionWrapper):
    """ Wrapper for Redis database connections """

    HELP_TEXT = "This connection accepts Redis commands (see: https://redis.io/commands). Enclose multi-word arguments in quotes."

    SEARCH_RANK = 1

    def execute_statement(self, statement: str):
        """ Return the results of executing a database statement

        :param statement: Statement to execute in the database
        """

        # Parse the statement
        tokens = dbreak.parser.tokenize(statement)

        # Execute the command
        result = self.raw_connection.execute_command(*tokens)

        # Return the result if any
        if result is not None:
            return [result]

    @classmethod
    def handles(cls, raw_connection: object) -> bool:
        """ Returns True if this class can wrap the given connection

        :param raw_connection: An unwrapped database connection to test
        """

        return type(raw_connection) is redis.Redis
