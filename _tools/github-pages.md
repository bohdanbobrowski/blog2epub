---
title: GitHub Pages
description: |+
    Websites for you and your projects.

    Hosted directly from your GitHub repository. Just edit, push, and your changes are live.
---

See the [pages.github.com](https://pages.github.com/) home to learn more.

With the standard flow, you don't need to run any CI steps yourself, locally or on GitHub. Just setup a repo that matches the minimum structure like this - [MichaelCurrin/simplest-jekyll](https://github.com/MichaelCurrin/simplest-jekyll).

Then whenever you commit on GitHub or push to GitHub from your machine, then GitHub will build and deploy your site.


## Limitations

Note the limitation that only certain Ruby gems are allowed and with locked versions. This limits the themes and plugins you can use. But there are plenty to use and a typical blog this be fine.

See [GitHub Pages Versions](https://pages.github.com/versions/)

When it comes to using themes, you can also use the Remote Themes plugin to pull in any theme from a GitHub URL, even if it is not on the standard gems list.


## Extending your build flow

If you end up wanting more complex build flows with your own build and CI steps or custom gems, then consider using GitHub Actions for your GH Pages site. Or [Netlify](https://netlify.com/) - which is a separate platform that integrates well with a GitHub repo and has a config of just a few lines. Unlike GitHub Pages which needs longer setup.
