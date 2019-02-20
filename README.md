##Earley's Implementation

This is an implementation of the Earley algorithm, a algorithm for parsing sentences given a grammar. This algorithm not only sees if the sentence is recognized by the grammar (if it's possible) but also gives the best parse by looking at the weights of each rule (lower weight means that it "costs" less to use, so it's considered a better parse). 

orig_earley.py is my original implementation, using just hashtables and the typical Earley structure. However, if you try running it with the wallstreet journal sentences and grammar, it takes a long time given the nature of the algorithm (where every applicable rule is placed on a stack). My faster_earley.py is my current attempt at speeding it up without sacrificing too much of the accuracy (done using some extra hashing and vocab specialization).

sentence1 contains the typical sentence "Papa ate the caviar with a spoon" while math contains some arithmetic equations. wallstreet_sentences include sentences and grammar from the WallStreet Journal. 

Example Usage:

'''
./orig_earley sentence1.gr sentence1.sen
'''