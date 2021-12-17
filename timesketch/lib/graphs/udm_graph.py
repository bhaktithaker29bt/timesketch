"""Graph plugin for Crest Graph."""

from timesketch.lib.graphs.interface import BaseGraphPlugin
from timesketch.lib.graphs import manager


class UDMGraph(BaseGraphPlugin):
    """Graph plugin for Windows logins."""

    NAME = 'UDM_Graph'
    DISPLAY_NAME = 'UDM Graph'

    def generate(self):
        """Generate the graph.

        Returns:
            Graph object instance.
        """
        query = 'tag:Box'
        return_fields = [
            'metadata.product_event_type', 'network.http.user_agent'
        ]

        events = self.event_stream(
            query_string=query, return_fields=return_fields)
        print("events",events)

        for event in events:
            product_event_type = event['_source'].get('metadata.product_event_type')
            user_agent = event['_source'].get('network.http.user_agent')

            product = self.graph.add_node(product_event_type, {'type': 'product'})
            user = self.graph.add_node(user_agent, {'type': 'user'})
            self.graph.add_edge(user, product)

        self.graph.commit()
        return self.graph


manager.GraphManager.register_graph(UDMGraph)
