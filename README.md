# RoadClosure

analyis.py calcola misure approssimate sul grafo. Richiede circa 3 minuti nel complesso

changeStatus.py cambia lo stato delle strade
Richiede:
"status" {close/open}
"mode" {amenity/id/name/random/all}
ed eventuali parametri in base a mode


() Esempio di analysis.py prima dopo la chiusura delle strade vicine agli ospedali (changeStatus.py close amenity hospital):

```
Running graph analysis...
- The network contains: 20004 junctions and 34263 routes
- There are 19555 junctions and 33504 routes currently open

- Weakly connected components: 15

- Approximate average shortest path length: 151.6 hops
- Approximate diameter: 410

- Approximate average distance: 5658.6 m
- Approximate max distance: 15110.5 m

- Within areas nearby closed roads, the average path length is 3582.5 m
        Whereas it was 3259.6 m before the road closure

- Considering roads within the 99th percentile of AADT as high traffic
        When all roads are open, the 99th percentile is: 8596.64 AADT
        When all roads are open, there are 342 high traffic routes
- Blocked off traffic is redirected to active routes
        In this scenario 367 routes are high traffic
```
