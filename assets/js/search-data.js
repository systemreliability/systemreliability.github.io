// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-cv",
          title: "CV",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "nav-publications",
          title: "Publications",
          description: "Peer-reviewed Journals, Thesis &amp; Proceedings of Conferences.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-projects",
          title: "Projects",
          description: "A growing collection of projects.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-teaching",
          title: "Teaching",
          description: "Courses I Taught or Codeveloped.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/teaching/";
          },
        },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-i-joined-the-structural-system-reliability-group-ssrg-at-snu",
          title: 'I joined the Structural System Reliability Group (SSRG) at SNU.',
          description: "",
          section: "News",},{id: "news-i-39-ve-completed-my-ph-d",
          title: 'I&amp;#39;ve completed my Ph.D.',
          description: "",
          section: "News",handler: () => {
              window.location.href = "/news/announcement_4/";
            },},{id: "news-i-joined-the-institute-of-construction-and-environmental-engineering-icee-at-snu-as-a-postdoctoral-researcher",
          title: 'I joined the Institute of Construction and Environmental Engineering (ICEE) at SNU as...',
          description: "",
          section: "News",},{id: "news-i-joined-the-engineering-risk-analysis-group-era-at-tum-as-a-postdoctoral-researcher",
          title: 'I joined the Engineering Risk Analysis Group (ERA) at TUM as a postdoctoral...',
          description: "",
          section: "News",},{id: "projects-postdoctoral-fellowship-program",
          title: 'Postdoctoral Fellowship Program',
          description: "Deep reinforcement learning-based optimal maintenance strategy for large-scale infrastructure networks under seismic risk",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},];
