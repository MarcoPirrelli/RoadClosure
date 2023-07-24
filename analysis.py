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
            session.run("""CALL gds.graph.project.cypher(
                        "graph",
                        "MATCH (n:RoadJunction) where n.status = 'active' RETURN id(n) AS id, n.lat AS lat, n.lon AS lon",
                        "MATCH ()-[r:ROUTE]->() with min(r.AADT) as min_AADT,max(r.AADT) as max_AADT,max(r.distance) as max_dist,min(r.distance) as min_dist MATCH (n)-[r:ROUTE]->(m) WHERE r.status = 'active' RETURN id(n) AS source, id(m) AS target, 0.5 * toFloat((r.AADT-min_AADT)/(max_AADT-min_AADT)) + 0.5 * toFloat((r.distance-min_dist)/(max_dist-min_dist)) as traffic, r.AADT as AADT, r.distance as distance, type(r) as type")""")

    def delete_projected_graph(self):
        with self.driver.session() as session:
            session.run("""
                        CALL gds.graph.drop('graph')
                        """)
            
    def create_full_projected_graph(self):
        with self.driver.session() as session:
            session.run("""CALL gds.graph.project.cypher(
                        "fullGraph",
                        "MATCH (n:RoadJunction) RETURN id(n) AS id, n.lat AS lat, n.lon AS lon",
                        "MATCH ()-[r:ROUTE]->() with min(r.AADT) as min_AADT,max(r.AADT) as max_AADT,max(r.distance) as max_dist,min(r.distance) as min_dist 
                        MATCH (n)-[r:ROUTE]->(m) RETURN id(n) AS source, id(m) AS target,
                        0.5 * toFloat((r.AADT-min_AADT)/(max_AADT-min_AADT)) + 0.5 * toFloat((r.distance-min_dist)/(max_dist-min_dist)) as traffic, r.AADT as AADT, r.distance as distance, type(r) as type")
                        """)

    def delete_full_projected_graph(self):
        with self.driver.session() as session:
            session.run("""
                        CALL gds.graph.drop('fullGraph')
                        """)        

    def count_streets(self):
        with self.driver.session() as session:
            result = session.run("""
                        match (j:RoadJunction)-[r:ROUTE]-() return count(distinct j), count(distinct r)
                        """)
            return result.values()[0]
            
    def count_open_streets(self):
        with self.driver.session() as session:
            result = session.run("""
                        match (j:RoadJunction)-[r:ROUTE]-() where j.status = "active" and r.status = "active" return count(distinct j), count(distinct r)
                        """)
            return result.values()[0]
        
    def wcc(self):
        with self.driver.session() as session:
            result = session.run("""
                        CALL gds.wcc.stats('graph') YIELD componentCount
                        """)
            return result.values()[0][0]
    
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
         
    def pathing_targeted(self):
        with self.driver.session() as session:
            result = session.run("""
                                match (closed:RoadJunction)-[:ROUTE {status:"closed"}]-()
                                match (nearby:RoadJunction {status:"active"})
                                with closed, nearby, point.distance(closed.location, nearby.location) as dist
                                where dist <= 500
                                with collect(distinct nearby) as a
                                match (r1:RoadJunction {status: "active"}) where r1 in a
                                with a, r1, rand() as rand order by rand limit 100
                                with collect(r1) as c1, a
                                match (r2:RoadJunction {status: "active"}) where r2 in a
                                with c1, r2, rand() as rand order by rand limit 100
                                unwind c1 as r1
                                match (r1), (r2) where r1 <> r2
                                with r1, r2, rand() as rand
                                order by rand limit 5000
                                
                                call gds.shortestPath.dijkstra.stream('fullGraph', {
                                    relationshipTypes: ['ROUTE'],
                                    sourceNode: id(r1),
                                    targetNode: id(r2),
                                    relationshipWeightProperty: 'distance'
                                })
                                yield totalCost as costBefore
                                call gds.shortestPath.dijkstra.stream('graph', {
                                    relationshipTypes: ['ROUTE'],
                                    sourceNode: id(r1),
                                    targetNode: id(r2),
                                    relationshipWeightProperty: 'distance'
                                })
                                yield totalCost as costAfter
                                return avg(costBefore) as averageBefore, avg(costAfter) as averageAfter
                                """)
            return result.values()[0]

if __name__ == "__main__":
    app = App()
    print("Running graph analysis...")
    app.create_projected_graph()
    app.create_full_projected_graph()

    jun_tot, rou_tot = app.count_streets()
    print("- The network contains: {} junctions and {} routes".format(int(jun_tot), int(rou_tot)))
    
    jun, rou = app.count_open_streets()
    if jun != jun_tot or rou!=rou_tot:
        print("- There are {} junctions and {} routes currently open".format(int(jun), int(rou)))
    else:
        print("- All junctions and routes are currently open")

    wcc = app.wcc() - 3
    print()
    print("- Weakly connected components: {}".format(int(wcc)))
    
    avg, max = app.pathing_hops()
    print()
    print("- Approximate average shortest path length: {:.1f} hops".format(avg))
    print("- Approximate diameter: {}".format(int(max)))


    avg, max = app.pathing_distance()
    print()
    print("- Approximate average distance: {:.1f} m".format(avg))
    print("- Approximate max distance: {:.1f} m".format(max))

    if jun != jun_tot or rou!=rou_tot:
        print()
        before, after = app.pathing_targeted()
        print("- Within areas nearby closed roads, the average path length is {:.1f} m".format(after))
        print("\tWhereas it was {:.1f} m before the road closure".format(before))

    app.delete_projected_graph()
    app.delete_full_projected_graph()
