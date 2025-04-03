---
layout: post
title: New Publication - Multi-scale seismic reliability assessment of networks by centrality-based selective recursive decomposition algorithm
date: 2021-02-20 16:30:00+0900
inline: false
related_posts: false
---

A journal paper, titled “Multi-scale seismic reliability assessment of networks by centrality-based selective recursive decomposition algorithm” was recently published in _Earthquake Engineering and Structural Dynamics_. The paper was co-authored by me and [Prof. Junho Song](https://systemreliability.wordpress.com/).

The permanent link via DOI number of the paper is [https://doi.org/10.1002/eqe.3447](https://doi.org/10.1002/eqe.3447). The full reference information is as follows.

---

> Lee, D., & Song, J. (2021). [Multi-scale seismic reliability assessment of networks by centrality-based selective recursive decomposition algorithm](https://doi.org/10.1002/eqe.3447). _Earthquake Engineering and Structural Dynamics_. Vol. 50, 2174-2194.

---

This paper proposed a new non-simulation-based algorithm to analyze the post-hazard network connectivity promptly but accurately. To this end, two algorithms were developed and utilized: (1) centrality-based selective recursive decomposition algorithm (CS-RDA), and (2) edge-betweenness algorithm. First, CS-RDA finds the most reliable path between an origin and destination (O/D) node pair, and decompose the network into subgraphs by removing the nodes in the path in order of network centrality. The O/D connectivity and its probability in subgraphs are recursively assessed until the width of bounds on the O/D connectivity converge to a certain level. In addition, a multi-scale analysis utilizing edge-betweenness algorithm enables CS-RDA to overcome the computational limitation in large-scale networks without compromising accuracy. The numerical examples including a hypothetical network and highway bridge networks in San Jose and San Diego demonstrate the performance and merits of the proposed methods.

ABSTRACT: As lifeline networks such as transportation or electricity networks in modern societies are intricately interlocked, a small number of components damaged by natural or man-made disasters can have a great impact on network performance. For this reason, it is essential to assure the capability of rapid assessment of network reliability to make prompt follow-up measures. Despite the rapid development of various algorithms and computing power, the capability is still limited due to computational cost for analyzing the connectivity of a single origin and destination (O/D) node pair in large-scale networks. Therefore, this paper introduces a new algorithm utilizing network centrality, termed “centrality-based selective recursive decomposition algorithm” (CS-RDA). By preferentially decomposing the node which is most likely to belong to the min-cut identified based on the betweenness centrality, the convergence of the bounds on the O/D connectivity can be expedited significantly. This paper also introduces a new multi-scale analysis approach termed “edge-betweenness algorithm.” The algorithm groups components such that its modularity is maximized, by sequentially removing edges that have the highest level of betweenness centrality. As a result, the reliability of large-scale networks can be accurately evaluated in a short time owing to the reduced complexity of the simplified network. The proposed methods are successfully demonstrated by a hypothetical network example, the highway bridge networks in San Jose and San Diego in California, USA.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news/news8_1.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Flowchart of the recursive decomposition algorithm
</div>
<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news/news8_2.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Hierarchical representation of the San Jose highway bridge network example for (a) bi-scale, and (b) tri-scale analysis
</div>
<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news/news8_3.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    (a) Bounds on the network reliability for the San Jose highway bridge network, and (b) bound widths in terms of the number of disjoint sets

</div>
