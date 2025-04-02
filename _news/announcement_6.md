---
layout: post
title: New Publication - Efficient seismic reliability and fragility analysis of lifeline networks using subset simulation
date: 2025-02-18 16:30:00+0900
inline: false
related_posts: announcement_3.md
---

A journal paper, titled “Efficient seismic reliability and fragility analysis of lifeline networks using subset simulation” was recently published in _Reliability Engineering & System Safety_. The paper was co-authored by me, [Prof. Ziqi Wang](https://coezresearch.wpenginepowered.com/) (UC Berkeley), and [Prof. Junho Song](https://systemreliability.wordpress.com) (SSRG), thanks to the visiting research program with the support of Brain Korea 21 Global Research Fellowship (Ministry of Education, South Korea).

The permanent link via DOI number of the paper is [https://doi.org/10.1016/j.ress.2025.110947](https://doi.org/10.1016/j.ress.2025.110947). The full reference information is as follows.

---

> Lee, D., Wang, Z., & Song, J. (2025). [Efficient seismic reliability and fragility analysis of lifeline networks using subset simulation](https://doi.org/10.1016/j.ress.2025.110947). _Reliability Engineering & System Safety_, 260: 110947.

---

This paper proposes two informative piecewise continuous limit-state functions (LSFs) for the reliability analysis of lifeline networks, thereby enabling the application of subset simulation (SS). Both LSF reformulations represent the same failure domain as the traditional binary LSF, while their function values at the safe domain differ; the first LSF quantifies the vulnerability of the most reliable path (RP) between the origin and destination nodes, whereas the other utilizes the shortest path (SP). The paper further proposes a specialized SS to generate network-level fragility curves by connecting intermediate failure events to the earthquake magnitude. The specialized SS can generate the network fragility curve in a single run. The sampling framework is extended to assess k-terminal or k-out-of-N reliability. The accuracy and efficiency of the proposed framework are tested and demonstrated by numerical examples using the Hamiltonian Monte Carlo-based SS (HMC-SS). The results confirm the accuracy and efficiency of the proposed network LSFs, as compared to other simulation-based methods directly applicable to binary LSFs. The RP-based LSF has higher accuracy, while the SP-based LSF requires less computation time.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news3_1.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Samples obtained from the (a) entire domain; (b) first subset; and (c) second subset using RP
</div>
<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news3_2.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Samples obtained from the (a) entire domain; (b) first subset; and (c) second subset using SP
</div>


ABSTRACT: Various simulation-based and analytical methods have been developed to evaluate the seismic fragilities of individual structures. However, the seismic safety and resilience of a community are substantially affected by network reliability, determined not only by component fragilities but also by network topology and commodity/information flows. However, seismic reliability analyses of networks often encounter significant challenges due to complex network topologies, interdependencies among ground motions, and low failure probabilities. This paper proposes to overcome these challenges by a variance-reduction method for network fragility analysis using subset simulation. The binary network limit-state function in the subset simulation is reformulated into more informative piecewise continuous functions. The proposed limit-state functions quantify the proximity of each sample to a potential network failure domain, thereby enabling the construction of specialized intermediate failure events, which can be utilized in subset simulation and other sequential Monte Carlo approaches. Moreover, by identifying an implicit relationship between intermediate failure events and seismic intensity, we propose a technique to obtain the entire network fragility curve with a single execution of specialized subset simulation. Numerical examples demonstrate that the proposed method can effectively evaluate system-level fragility for large-scale networks.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/news3_3.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    (a) Comparison of generated seismic fragility curves of San Jose highway bridge network; and (b) multi-state network fragility curves obtained by specialized HMC-SS.
</div>
