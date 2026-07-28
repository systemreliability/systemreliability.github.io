---
layout: page
permalink: /it/publications/
title: Pubblicazioni
description: Articoli scientifici sottoposti a revisione paritaria, tesi e atti di conferenze.
nav: true
nav_order: 2

lang: it
translation_key: publications
---

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}

<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> Aggiornamento automatico il {{ site.data.citations.metadata.last_updated | date: "%B %d, %Y" }}
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>

<script src="{{ '/assets/js/publication-badges.js' | relative_url }}?v={{ site.github.build_revision | default: site.time | date: '%s' }}"></script>
