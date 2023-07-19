from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

class App:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def reopen_streets(self):
        with self.driver.session() as session:
            session.run("""match (j:RoadJunction)-[r:ROUTE]-() set j.status = 'active', r.status = 'active'""")

        

if __name__ == "__main__":
    app = App()
    app.reopen_streets()
    print("Streets reopened")

