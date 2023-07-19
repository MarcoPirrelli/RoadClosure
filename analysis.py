from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

class App:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def create_projected_graph(self):
        with self.driver.session() as session:
            path = session.read_transaction(self._projected_graph,)

    @staticmethod
    def _projected_graph(tx,):
        result = tx.run("""CALL gds.graph.project.cypher(
                        "graph",
                        "MATCH (n:RoadJunction) where n.status = 'active' RETURN id(n) AS id, n.lat AS lat, n.lon AS lon",
                        "MATCH ()-[r:ROUTE]->() with min(r.AADT) as min_AADT,max(r.AADT) as max_AADT,max(r.distance) as max_dist,min(r.distance) as min_dist MATCH (n)-[r:ROUTE]->(m) WHERE r.status = 'active' RETURN id(n) AS source, id(m) AS target, 0.5 * toFloat((r.AADT-min_AADT)/(max_AADT-min_AADT)) + 0.5 * toFloat((r.distance-min_dist)/(max_dist-min_dist)) as traffic, r.AADT as AADT, r.distance as distance, type(r) as type")""")
        return result

    def delete_projected_graph(self):
        with self.driver.session() as session:
            path = session.read_transaction(self._drop_projected_graph)

    @staticmethod
    def _drop_projected_graph(tx):
        result = tx.run("""
                CALL gds.graph.drop('graph')
                        """)
        return result

    def pathing_hops(self):
        with self.driver.session() as session:
            result = session.run("""
                                match (r1:RoadJunction {status: "active"}) with r1, rand() as rand order by rand limit 200
                                with collect(r1) as c1
                                match (r2:RoadJunction {status: "active"}) with c1, r2, rand() as rand order by rand limit 200
                                unwind c1 as r1
                                match (r1), (r2) where r1 <> r2
                                with r1, r2, rand() as rand
                                order by rand limit 10000
                                call gds.shortestPath.dijkstra.stream('graph', {
                                    relationshipTypes: ['ROUTE'],
                                    sourceNode: id(r1),
                                    targetNode: id(r2)
                                })
                                yield totalCost
                                return avg(totalCost) as average, max(totalCost) as max""")

            return result.values()[0]
        
    def pathing_distance(self):
         with self.driver.session() as session:
            result = session.run("""
                                match (r1:RoadJunction {status: "active"}) with r1, rand() as rand order by rand limit 200
                                with collect(r1) as c1
                                match (r2:RoadJunction {status: "active"}) with c1, r2, rand() as rand order by rand limit 200
                                unwind c1 as r1
                                match (r1), (r2) where r1 <> r2
                                with r1, r2, rand() as rand
                                order by rand limit 10000
                                call gds.shortestPath.dijkstra.stream('graph', {
                                    relationshipTypes: ['ROUTE'],
                                    sourceNode: id(r1),
                                    targetNode: id(r2),
                                    relationshipWeightProperty: 'distance'
                                })
                                yield totalCost
                                return avg(totalCost) as average, max(totalCost) as max""")
            return result.values()[0]

if __name__ == "__main__":
    app = App()
    print("Running graph analysis...")
    app.create_projected_graph()

    avg, max = app.pathing_hops()
    print("- Approximate average shortest path length: {:.1f} hops".format(avg))
    print("- Approximate diameter: {:d}".format(int(max)))

    print()

    avg, max = app.pathing_distance()
    print("- Approximate average distance: {:.1f} m".format(avg))
    print("- Approximate max distance: {:.1f} m".format(max))

    app.delete_projected_graph()

