---
layout: page
title: Postdoctoral Fellowship Program
description: Deep reinforcement learning-based optimal maintenance strategy for large-scale infrastructure networks under seismic risk
img: assets/img/Fig1_1.png
importance: 1
category: Research
related_publications: true
---

Infrastructure networks, such as transportation, gas, and electricity networks, are the backbone of modern society. These networks face natural hazards that are intensifying with climate change. The reliability and operability after a disaster directly impact public safety and have significant socio-economic consequences. Despite growing risks from natural and man-made hazards, the budget allocated to maintaining these networks is insufficient to ensure their robustness. Furthermore, there is a lack of comprehensive research on the optimal trade-off between the risks and budgetary limitations. Most infrastructure network maintenance policies solely address deterioration-related failures, ignoring the risk assessment related to natural disasters. As a result, infrastructure networks are vulnerable to unforeseen disasters, which can cause catastrophic damage. To make appropriate maintenance decisions and budget allocations for sustainable infrastructure, it is imperative to not only assess network reliability accurately but also to identify optimal network-level maintenance options to minimize the potential risk of disaster.

The proposed research aims to develop methods and algorithms for optimizing network maintenance policies over their lifetimes by considering the risk of natural disasters, specifically earthquakes. The key question is how to effectively overcome combinatorial explosions while minimizing efficiency losses. This general goal translates into the following specific research objectives: (1) to develop optimal sequential decision-making for managing infrastructure networks under potential seismic risk; (2) to devise a multi-agent reinforcement learning (MARL)-based network maintenance policy with hierarchical network modeling, which is applicable to large-scale networks; and (3) to test and demonstrate the application of both developed methodologies on real-world infrastructure networks. Objective 1 is approached with advanced sampling techniques to accurately quantify seismic risk {% cite lee2025efficient %} for optimal policies, objective 2 by a combination of hierarchically modeled networks with MARL for high scalability with respect to network size {% cite lee2023risk %}. For the hierarchical network modeling, a network simplification approach will be adopted to decrease the computational complexity to a more manageable level. Consequently, this research will contribute to a more “hazard-resilient” society by addressing risks and uncertainties in maintenance planning and streamlining civil infrastructure management budgets.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/Fig1_1.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/Fig1_2.png" title="example image" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Figure 1. Schematic structure of the optimal sequential decision-making.
</div>

This project is funded by the Postdoctoral Fellowship Program (nurturing next-generation researchers), supported by National Research Foundation of Korea (NRF).
