---
layout: page
title: Projects
permalink: /projects/
description: 
nav: true
nav_order: 3
---

<div class="projects">
  {% assign sorted_projects = site.projects | sort: "date" | reverse %}
  {% for project in sorted_projects %}
    <div class="project-entry" style="margin-bottom: 60px;">
      <h2>{{ project.title }}</h2>
      
      <div class="project-meta" style="margin-bottom: 20px; font-size: 0.95rem; color: var(--global-text-color-light);">
        {% if project.grant_period %}
        <div><strong>Grant Period:</strong> {{ project.grant_period }}</div>
        {% endif %}
        {% if project.funder %}
        <div><strong>Funder:</strong> {{ project.funder }}</div>
        {% endif %}
        {% if project.team %}
        <div style="margin-top: 5px;">
          <strong>Team:</strong>
          <ul style="margin-bottom: 0; padding-left: 20px;">
            {% if project.team.pi %}<li><em>PIs:</em> {{ project.team.pi }}</li>{% endif %}
            {% if project.team.postdocs %}<li><em>Postdocs:</em> {{ project.team.postdocs }}</li>{% endif %}
            {% if project.team.phd_students %}<li><em>PhD students:</em> {{ project.team.phd_students }}</li>{% endif %}
            {% if project.team.undergrads %}<li><em>Undergrads:</em> {{ project.team.undergrads }}</li>{% endif %}
          </ul>
        </div>
        {% elsif project.people_involved %}
        <div><strong>People Involved:</strong> {{ project.people_involved }}</div>
        {% endif %}
      </div>

      {% if project.img %}
        <div class="project-img" style="margin-bottom: 20px;">
          <img src="{{ project.img | relative_url }}" alt="Graphical abstract for {{ project.title }}" class="img-fluid rounded z-depth-1" style="max-height: 400px; width: auto;">
        </div>
      {% endif %}
      
      <div class="project-content">
        {{ project.content }}
      </div>
    </div>
    {% unless forloop.last %}
      <hr style="margin-bottom: 60px;">
    {% endunless %}
  {% endfor %}
</div>
