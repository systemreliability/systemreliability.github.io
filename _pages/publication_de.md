---
layout: page
permalink: /de/publications/
title: Publikationen
description: Begutachtete Zeitschriftenartikel, Dissertation und Konferenzbeiträge.
nav: true
nav_order: 2
lang: de
translation_key: publications
---

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}

<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> Automatisches Update am {{ site.data.citations.metadata.last_updated | date: "%B %d, %Y" }}
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>

<script src="{{ '/assets/js/publication-badges.js' | relative_url }}?v={{ site.github.build_revision | default: site.time | date: '%s' }}"></script>