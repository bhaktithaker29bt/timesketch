"""Graph plugin for Crest Graph."""

from timesketch.lib.graphs.interface import BaseGraphPlugin
from timesketch.lib.graphs import manager


class CrestGraph(BaseGraphPlugin):
    """Graph plugin for Windows logins."""

    NAME = 'Crest_Graph'
    DISPLAY_NAME = 'Crest Graph'

    def generate(self):
        """Generate the graph.

        Returns:
            Graph object instance.
        """
        query = 'tag:logon-event'
        return_fields = [
            'computer_name', 'username', 'logon_type', 'logon_process'
        ]

        events = self.event_stream(
            query_string=query, return_fields=return_fields)

        for event in events:
            computer_name = event['_source'].get('computer_name')
            username = event['_source'].get('username')
            logon_type = event['_source'].get('logon_type')

            computer = self.graph.add_node(computer_name, {'type': 'computer'})
            user = self.graph.add_node(username, {'type': 'user'})
            self.graph.add_edge(user, computer, logon_type, event)

        self.graph.commit()

        return self.graph


manager.GraphManager.register_graph(CrestGraph)
