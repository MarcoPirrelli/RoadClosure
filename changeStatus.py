from neo4j import GraphDatabase
import argparse

URI = "neo4j://localhost:7687"
USER = "neo4j"
PASSWORD = "password"

class App:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    def close(self):
        self.driver.close()

    def change_status_amenity(self, status, amenity):
        with self.driver.session() as session:
            if status == "open":
                g_status = "active"
            elif status == "close":
                g_status = "closed"
            else:
                print("Error: Invalid status")
                exit(1)
            result = session.run("""
                                match (t:Tag) where t.amenity = $amenity
                                match (t)<-[:TAGS]-()-[:MEMBER]->(:OSMWayNode)<-[:NEAR]-(j:RoadJunction)-[r:ROUTE]-()
                                set j.status = $status, r.status = $status
                                return count(distinct j) as junctions, count(distinct r) as routes""", amenity=amenity, status=g_status)

            return result.values()[0]
    
    def change_status_id(self, status, id):
        with self.driver.session() as session:
            if status == "open":
                g_status = "active"
            elif status == "close":
                g_status = "closed"
            else:
                print("Error: Invalid status")
                exit(1)

            result = session.run("""MATCH (n)-[r:ROUTE]-() 
                                    WHERE r.osmid = $osmid  
                                    SET r.status = $status 
                                    """,osmid=id, status=g_status)
            
    def change_status_name(self, status, name):
        with self.driver.session() as session:
            if status == "open":
                g_status = "active"
            elif status == "close":
                g_status = "closed"
            else:
                print("Error: Invalid status")
                exit(1)

            result = session.run("""
                                MATCH ()-[r:ROUTE]-() 
                                WHERE r.name = $street  
                                SET r.status=$status
                                """,street=name, status=g_status)
        
    def close_random(self, n):
        with self.driver.session() as session:
            result = session.run("""
                                match ()-[r:ROUTE]-()
                                with distinct r
                                with r, rand() as rand order by rand limit $n
                                set r.status = 'closed'""", n=n)

    def open_all(self):
        with self.driver.session() as session:
            session.run("""match (j:RoadJunction)-[r:ROUTE]-() set j.status = 'active', r.status = 'active'""")
        
def create_parser():
    parser = argparse.ArgumentParser(description='Changes the status of streets')
    status_sp = parser.add_subparsers(dest="status", required=True,
                                        help="""
                                        Status to be set. Either 'open' or 'close'
                                        """)
    status_close_p = status_sp.add_parser("close")

    status_close_sp = status_close_p.add_subparsers(dest="mode", required=True,
                                        help="Closing mode. Either 'amenity', 'random', 'id' or 'street_name'")
    status_close_amenity_p = status_close_sp.add_parser("amenity")
    status_close_amenity_p.add_argument('type', type=str, help="Amenity type")

    status_close_random_p = status_close_sp.add_parser("random")
    status_close_random_p.add_argument('n', type=int, help="Number of streets to close")

    status_close_id_p = status_close_sp.add_parser("id")
    status_close_id_p.add_argument('id', type=str, help="Osmid of street to close")

    status_close_name_p = status_close_sp.add_parser("street_name")
    status_close_name_p.add_argument('street_name', type=str, help="Name of street to close")
    
    status_open_p = status_sp.add_parser("open")
    status_open_sp = status_open_p.add_subparsers(dest="mode", required=True,
                                        help="Opening mode. Either 'amenity', 'all', 'id, 'name'")
    
    status_open_amenity_p = status_open_sp.add_parser("amenity")
    status_open_amenity_p.add_argument('type', type=str, help="Amenity type")

    status_open_sp.add_parser("all")

    status_open_id_p = status_open_sp.add_parser("id")
    status_open_id_p.add_argument('id', type=str, help="Osmid of street to open")

    status_open_name_p = status_open_sp.add_parser("street_name")
    status_open_name_p.add_argument('street_name', type=str, help="Name of street to open")
    
    return parser

def main(args=None):
    parser = create_parser()
    
    options = parser.parse_args(args=args)

    app = App()

    if options.mode == "amenity":
        jun, routes = app.change_status_amenity(options.status, options.type)
        if options.status == "open":
            print("Opened {} junctions and {} routes".format(jun, routes))
        elif options.status == "close":
            print("Closed {} junctions and {} routes".format(jun, routes))

    elif options.mode == "id":
        app.change_status_id(options.status, options.id)

    elif options.mode == "street_name":
        app.change_status_name(options.status, options.street_name)

    elif options.status == "close" and options.mode == "random":
        app.close_random(options.n)
        print("Closed {} routes".format(options.n))

    elif options.status == "open" and options.mode == "all":
        app.open_all()
        print("All streets and junctions reopened")

if __name__ == "__main__":
    main()

