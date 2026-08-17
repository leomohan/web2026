# Web 2026

A personal website featuring articles, stories, books, and multimedia content.

## Overview

Web2026 is a dynamic portfolio and content distribution website showcasing:
- Articles and blog posts
- Published books and stories
- Technology and business insights
- Various multimedia content

## Live Site

Visit: https://leomohan.github.io/web2026/ or check CNAME for current domain

## Features

- Multiple content categories:
  - Technology
  - Business
  - Philosophy
  - General insights
  - Fiction and stories
  - Travel and experiences
  
- Content management system
- Responsive design
- SEO optimization (robots.txt, sitemap.xml)

## Technologies Used

- HTML5
- CSS3
- JavaScript
- Python (build scripts)

## Local Development

```bash
# Clone the repository
git clone https://github.com/leomohan/web2026.git
cd web2026

# Run the build script (requires Python)
python build.py

# Start local server
python -m http.server 8000
```

Then visit `http://localhost:8000`

## Project Structure

```
.
├── index.html                 # Main landing page
├── articles.html              # Articles listing
├── books.html                 # Books catalog
├── technology.html            # Tech articles
├── business.html              # Business insights
├── build.py                   # Build automation
├── manager.py                 # Content management
├── assets/                    # Images and resources
├── data/                      # Content data
├── robots.txt                 # SEO configuration
├── sitemap.xml               # Site map
└── CNAME                      # Custom domain
```

## Content Categories

- **About & Bio** - Personal information
- **Articles** - In-depth articles and essays
- **Books** - Published works and stories
- **Technology** - Tech-related content
- **Business** - Business and management insights
- **Philosophy** - Philosophical explorations
- **Podcasts** - Audio content
- **News** - Latest updates
- **Gallery** - Visual content

## Build & Deployment

```bash
# Build the site
python build.py

# Manage content
python manager.py
```

See UPDATING.md for detailed update instructions.

## SEO

- Sitemap: /sitemap.xml
- Robots: /robots.txt
- Mobile responsive
- OpenGraph metadata

## License

*Add license information*

## Author

Leo Mohan

---

**Last Updated:** July 2026
