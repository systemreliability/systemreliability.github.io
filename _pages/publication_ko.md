---
layout: page
permalink: /ko/publications/
title: 연구 성과
description: 학위논문, 국제학술지 논문 및 학술대회 발표
nav: true
nav_order: 2

lang: ko
translation_key: publications
---

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}

<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> {{ site.data.citations.metadata.last_updated | date: "%B %d, %Y" }}에 자동 업데이트
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>

<script src="{{ '/assets/js/publication-badges.js' | relative_url }}?v={{ site.github.build_revision | default: site.time | date: '%s' }}"></script>