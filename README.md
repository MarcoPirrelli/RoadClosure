# RoadClosure

analyis.py calcola misure approssimate sul grafo. Richiede circa 3 minuti nel complesso

changeStatus.py cambia lo stato delle strade
Richiede:
"status" {close/open}
"mode" {amenity/id/name/random/all}
ed eventuali parametri in base a mode

() Esempio di analysis.py prima della chiusura:

Running graph analysis...
- The network contains: 20004 junctions and 34263 routes
- All junctions and routes are currently open

- Weakly connected components: 1

- Approximate average shortest path length: 148.7 hops
- Approximate diameter: 401

- Approximate average distance: 5486.1 m
- Approximate max distance: 15846.3 m

() Esempio di analysis.py prima dopo la chiusura delle strade vicine agli ospedali (changeStatus.py close amenity hospital):

Running graph analysis...
- The network contains: 20004 junctions and 34263 routes
- There are 19555 junctions and 33504 routes currently open

- Weakly connected components: 15

- Approximate average shortest path length: 160.3 hops
- Approximate diameter: 409

- Approximate average distance: 5798.0 m
- Approximate max distance: 16058.1 m   

- Within areas nearby closed roads, the average path length is 3614.3 m
        Whereas it was 3284.4 m before the road closure
