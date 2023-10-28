source "https://rubygems.org"

gem "jekyll", "~> 3.9"
gem "kramdown-parser-gfm", "~> 1.1"  # Required for Jekyll 3.9 (not 3.8 or 4)
gem "webrick", "~> 1.7"  # Ruby 3 support

gem "minima", "~> 2.5.1"

group :jekyll_plugins do
  gem "jekyll-sitemap", "~> 1.4"
end

# Windows

# The zoneinfo files are missing, so bundle the tzinfo-data gem and associated
# library.
install_if -> { RUBY_PLATFORM =~ %r!mingw|mswin|java! } do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

# Performance-booster for watching directories and fix for livereload.
gem "wdm", "~> 0.1.0", :install_if => Gem.win_platform?
