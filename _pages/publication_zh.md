---
layout: page
permalink: /zh/publications/
title: 学术成果
description: 同行评审期刊论文、学位论文及会议论文。
nav: true
nav_order: 2
lang: zh
translation_key: publications
---

<!-- _pages/publications.md -->

{% if site.data.citations.metadata.last_updated %}

<p class="text-muted mt-3 small">
  <i class="fas fa-sync-alt mr-1"></i> 最近更新： {{ site.data.citations.metadata.last_updated | date: "%B %d, %Y" }}
</p>
{% endif %}

<div class="publications">
{% bibliography %}

</div>

<script src="{{ '/assets/js/publication-badges.js' | relative_url }}?v={{ site.github.build_revision | default: site.time | date: '%s' }}"></script>