We employ a caching strategy to enhance query speed, with a First-In-First-Out (FIFO) replacement policy. 
To implement cache replacement, we manage a FIFO queue.

In each query, we initially search within the cache. 
In the event of a cache miss, we replace the oldest block if the cache is full, and subsequently append the missed block to the cache.

You can find the boosted *_matcher.py in each matcher_server