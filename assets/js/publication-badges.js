(() => {
  const getDoi = (entry) => {
    const doiLink = entry.querySelector('.links a[href^="https://doi.org/"]');
    if (!doiLink) return null;
    return doiLink.href.replace(/^https:\/\/doi\.org\//, "").trim();
  };

  const ensureBadgeRow = (entry) => {
    let badges = entry.querySelector(".badges");
    if (badges) return badges;

    const links = entry.querySelector(".links");
    if (!links) return null;

    badges = document.createElement("div");
    badges.className = "badges d-inline-flex align-items-center";
    badges.style.gap = "0.35rem";
    links.insertAdjacentElement("afterend", badges);
    return badges;
  };

  const addAltmetricBadge = (badges, doi) => {
    if (badges.querySelector(".altmetric-embed")) return;

    const badge = document.createElement("span");
    badge.className = "altmetric-embed";
    badge.dataset.badgeType = "2";
    badge.dataset.badgePopover = "right";
    badge.dataset.doi = doi;
    badges.prepend(badge);
  };

  const addOpenAlexBadge = (badges, doi) => {
    if (badges.querySelector(".openalex-badge")) return;

    const apiUrl = `https://api.openalex.org/works/https://doi.org/${doi}?select=cited_by_count`;
    const link = document.createElement("a");
    link.className = "openalex-badge";
    link.href = `https://openalex.org/search?q=${encodeURIComponent(
      `doi:${doi}`
    )}`;
    link.setAttribute("aria-label", "OpenAlex link");
    link.setAttribute("role", "button");
    link.rel = "external nofollow noopener";
    link.target = "_blank";

    const image = document.createElement("img");
    image.src = `https://img.shields.io/badge/dynamic/json?url=${encodeURIComponent(
      apiUrl
    )}&query=$.cited_by_count&label=OpenAlex&color=2f7f6f&labelColor=beige`;
    image.alt = "OpenAlex citation count";

    link.appendChild(image);
    badges.appendChild(link);
  };

  document
    .querySelectorAll(".bibliography li > .row > [id]")
    .forEach((entry) => {
      const doi = getDoi(entry);
      if (!doi) return;

      const badges = ensureBadgeRow(entry);
      if (!badges) return;

      addAltmetricBadge(badges, doi);
      addOpenAlexBadge(badges, doi);
    });
})();
