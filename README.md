# RoadClosure

analyis.py calcola misure approssimate sul grafo. Richiede circa 3 minuti nel complesso

changeStatus.py cambia lo stato delle strade
Richiede:
"status" {close/open}
"mode" {amenity/id/name/random/all}
ed eventuali parametri in base a mode


<> Esempio di analysis.py prima dopo la chiusura delle strade vicine agli ospedali (changeStatus.py close amenity hospital):

```
Running graph analysis...
- The network contains: 20004 junctions and 34263 routes
- There are 19555 junctions and 33504 routes currently open

- Weakly connected components: 15

- Approximate average shortest path length: 159.0 hops
- Approximate diameter: 407

- Approximate average distance: 6015.3 m
- Approximate max distance: 18060.1 m

- Within areas nearby closed roads, the average path length is 3764.4 m
        Whereas it was 3479.5 m before the road closure

- Considering roads within the 99th percentile of AADT as high traffic
        When all roads are open, the 99th percentile is: 8596.6 AADT
        When all roads are open, there are 342 high traffic routes
- Blocked off traffic is redirected to active routes
        In this scenario 707 routes have increased traffic, with a total length of 29.7 km
        354 routes are now high traffic
        The 99th percentile has shifted to 8736.4 AADT (101.6% compared to before)
        The closed road that impacted the most nearby streets is Via Codroipo (osmid=26831593), with 59 streets affected
```
