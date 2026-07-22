---
layout: page
permalink: /repositories/
title: Repositories
description: Collection of repositories for teaching and research projects
nav: true
nav_order: 4
---

## GitHub Profile

<div class="repo p-2 text-center">
  <a href="https://github.com/karkman" target="_blank">
    <i class="fa-brands fa-github fa-3x"></i>
    <h6 class="mt-2">github.com/karkman</h6>
  </a>
</div>

---

## Repositories

<div class="row row-cols-1 row-cols-md-3 mt-3">
  {% for repo in site.data.repositories.github_repos %}
    {% assign repo_url = repo | split: '/' %}
    {% assign description = site.data.repositories.repo_descriptions[repo] %}
    <div class="col mb-3">
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">
            <a href="https://github.com/{{ repo }}" target="_blank">
              <i class="fa-brands fa-github"></i> {{ repo_url[1] }}
            </a>
          </h5>
          {% if description %}
            <p class="card-text text-muted">{{ description }}</p>
          {% endif %}
          <p class="card-text">
            <a href="https://github.com/{{ repo }}" target="_blank" class="btn btn-outline-primary btn-sm mt-2">
              View on GitHub <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
          </p>
        </div>
      </div>
    </div>
  {% endfor %}
</div>
