---
layout: page
permalink: /publications/
title: Publications
description: Peer-reviewed Journals, Thesis & Proceedings of Conferences.
nav: true
nav_order: 2
---

<script async src="https://cdn.plu.mx/widget-popup.js"></script>

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}

<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> Automatically updated on {{ site.data.citations.metadata.last_updated | date: "%B %d, %Y" }}
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>

<script src="{{ '/assets/js/publication-badges.js' | relative_url }}?v={{ site.github.build_revision | default: site.time | date: '%s' }}"></script>
