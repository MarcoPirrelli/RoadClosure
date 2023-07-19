from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

class App:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def close_streets(self):
        with self.driver.session() as session:
            result = session.run("""
                                match (t:Tag) where t.amenity in ["place_of_worship", "hospital", "police"]
                                match (t)<-[:TAGS]-()-[:MEMBER]->(:OSMWayNode)<-[:NEAR]-(j:RoadJunction)-[r:ROUTE]-()
                                set j.status = "closed", r.status = "closed"
                                return count(distinct j) as junctions, count(distinct r) as routes""")

            return result.values()[0]
        

if __name__ == "__main__":
    app = App()
    jun, routes = app.close_streets()
    print("Closed {} junctions and {} routes".format(jun, routes))

