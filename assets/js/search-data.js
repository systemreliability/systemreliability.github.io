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
        },{id: "nav-cv",
          title: "CV",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/de/cv/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/it/cv/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/ko/cv/";
          },
        },{id: "nav-简历",
          title: "简历",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/zh/cv/";
          },
        },{id: "nav-publikationen",
          title: "Publikationen",
          description: "Begutachtete Zeitschriftenartikel, Dissertation und Konferenzbeiträge.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/de/publications/";
          },
        },{id: "nav-pubblicazioni",
          title: "Pubblicazioni",
          description: "Articoli scientifici sottoposti a revisione paritaria, tesi e atti di conferenze.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/it/publications/";
          },
        },{id: "nav-연구-성과",
          title: "연구 성과",
          description: "학위논문, 국제학술지 논문 및 학술대회 발표",
          section: "Navigation",
          handler: () => {
            window.location.href = "/ko/publications/";
          },
        },{id: "nav-学术成果",
          title: "学术成果",
          description: "同行评审期刊论文、学位论文及会议论文。",
          section: "Navigation",
          handler: () => {
            window.location.href = "/zh/publications/";
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
        },{id: "nav-projekte",
          title: "Projekte",
          description: "Eine fortlaufend aktualisierte Sammlung meiner Forschungsprojekte.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/de/projects/";
          },
        },{id: "nav-progetti",
          title: "Progetti",
          description: "Una raccolta in continuo aggiornamento di progetti di ricerca.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/it/projects/";
          },
        },{id: "nav-연구",
          title: "연구",
          description: "주요 연구 프로젝트 및 연구 활동",
          section: "Navigation",
          handler: () => {
            window.location.href = "/ko/projects/";
          },
        },{id: "nav-研究项目",
          title: "研究项目",
          description: "持续更新的研究项目合集。",
          section: "Navigation",
          handler: () => {
            window.location.href = "/zh/projects/";
          },
        },{id: "nav-teaching",
          title: "Teaching",
          description: "Courses that I Taught or Codeveloped.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/teaching/";
          },
        },{id: "nav-lehre",
          title: "Lehre",
          description: "Lehrveranstaltungen, die ich gehalten oder mitentwickelt habe.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/de/teaching/";
          },
        },{id: "nav-didattica",
          title: "Didattica",
          description: "Attività didattiche e corsi.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/it/teaching/";
          },
        },{id: "nav-교육",
          title: "교육",
          description: "강의 및 교육 활동",
          section: "Navigation",
          handler: () => {
            window.location.href = "/ko/teaching/";
          },
        },{id: "nav-教学",
          title: "教学",
          description: "本人讲授或参与开发的课程。",
          section: "Navigation",
          handler: () => {
            window.location.href = "/zh/teaching/";
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
              window.location.href = "/news/announcement_2/";
            },},{id: "news-i-joined-the-institute-of-construction-and-environmental-engineering-icee-at-snu-as-a-postdoctoral-researcher",
          title: 'I joined the Institute of Construction and Environmental Engineering (ICEE) at SNU as...',
          description: "",
          section: "News",},{id: "news-i-joined-the-engineering-risk-analysis-group-era-at-tum-as-a-postdoctoral-researcher",
          title: 'I joined the Engineering Risk Analysis Group (ERA) at TUM as a postdoctoral...',
          description: "",
          section: "News",},{id: "news-i-joined-the-department-of-civil-environmental-and-mechanical-engineering-dicam-at-unitn-as-a-postdoctoral-researcher",
          title: 'I joined the Department of civil, environmental and mechanical engineering (DICAM) at UNITN...',
          description: "",
          section: "News",},{id: "projects-postdoctoral-fellowship-program",
          title: 'Postdoctoral Fellowship Program',
          description: "Deep reinforcement learning-based optimal maintenance strategy for large-scale infrastructure networks under seismic risk",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
