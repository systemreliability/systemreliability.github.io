---
layout: page
permalink: /publications/
title: Publications
description: Peer-reviewed Journals, Thesis & Proceedings of Conferences.
nav: true
nav_order: 2
---

<script type="text/javascript" src="//cdn.plu.mx/widget-popup.js"></script>

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}
<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> Automatically updated on {{ site.data.citations.metadata.last_updated }}
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>
