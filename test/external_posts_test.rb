require 'minitest/autorun'
require 'tmpdir'
require 'fileutils'
require 'json'
require 'open3'
require 'jekyll'

ROOT = File.expand_path(ENV.fetch('SECURITY_TEST_ROOT', '..'), __dir__)
require File.join(ROOT, '_plugins/external-posts')

class ExternalPostsTest < Minitest::Test
  def setup
    @dir = Dir.mktmpdir('external-posts-test')
    FileUtils.mkdir_p(File.join(@dir, '_layouts'))
    File.write(File.join(@dir, '_layouts', 'post.html'), '<h1>{{ page.title }}</h1>{{ content }}')
    @site = Jekyll::Site.new(Jekyll.configuration(
      'source' => @dir, 'destination' => File.join(@dir, '_site'),
      'plugins_dir' => [], 'quiet' => true, 'permalink' => '/blog/:year/:title/',
      'markdown' => 'kramdown', 'kramdown' => { 'input' => 'GFM' },
      'defaults' => [{ 'scope' => { 'type' => 'posts' }, 'values' => { 'layout' => 'post' } }]
    ))
    @site.read
    @generator = ExternalPosts::ExternalPostsGenerator.new
  end

  def teardown
    FileUtils.remove_entry(@dir)
  end

  def import(title: 'Research & results', summary: 'An ordinary summary', source_name: 'Publisher',
             url: 'https://example.org/paper?a=1&b=2', body: '**Useful** [paper](https://example.org/paper)')
    @generator.create_document(@site, source_name, url,
      title: title, summary: summary, content: body, published: Time.utc(2025, 1, 2))
    @site.posts.docs.last
  end

  def render_file(path, payload)
    source = File.read(File.join(ROOT, path)).sub(/\A---\s*\n.*?\n---\s*\n/m, '')
    Liquid::Template.parse(source).render!(payload, registers: { site: @site })
  end

  def test_imported_metadata_stays_text_in_homepage_and_archive
    title = '<img src=x onerror="globalThis.compromised=1"> Research'
    doc = import(title: title, summary: '<svg onload="globalThis.compromised=1"></svg>')
    payload = { 'site' => { 'posts' => [doc.to_liquid] }, 'page' => { 'latest_posts' => { 'limit' => 6 } } }
    homepage = Nokogiri::HTML.fragment(render_file('_includes/latest_posts.liquid', payload))
    assert_empty homepage.css('img, [onerror], [onload]')
    assert_equal title, homepage.at_css('a').text
    assert_equal 'https://example.org/paper?a=1&b=2', homepage.at_css('a')['href']
    archive = Nokogiri::HTML.fragment(render_file('_layouts/archive.liquid', {
      'page' => { 'documents' => [doc.to_liquid] }, 'site' => {} }))
    assert_empty archive.css('img, [onerror], [onload]')
    assert_equal title, archive.at_css('a').text
  end

  def test_rss_parser_to_importer_preserves_inert_metadata
    feed = Feedjira.parse('<rss version="2.0"><channel><title>Feed</title><link>https://example.org</link><description>Feed</description><item><title><![CDATA[<img src=x onerror=alert(1)>]]></title><link>https://example.org/post</link><description><![CDATA[<script>alert(1)</script>]]></description><pubDate>Thu, 02 Jan 2025 00:00:00 GMT</pubDate></item></channel></rss>')
    @generator.process_entries(@site, { 'name' => 'Publisher' }, feed.entries)
    doc = @site.posts.docs.last
    html = render_file('_includes/latest_posts.liquid', { 'site' => { 'posts' => [doc.to_liquid] }, 'page' => { 'latest_posts' => { 'limit' => 6 } } })
    assert_empty Nokogiri::HTML.fragment(html).css('img, [onerror]')
    assert_equal '<script>alert(1)</script>', doc.data['description']
  end

  def test_blog_and_related_listings_escape_external_metadata
    doc = import(title: '<img src=x onerror=alert(1)>', summary: '<svg onload=alert(1)>', source_name: '')
    payload = { 'site' => { 'posts' => [doc.to_liquid], 'related_posts' => [doc.to_liquid],
      'related_blog_posts' => { 'max_related' => 5 } }, 'page' => { 'pagination' => { 'enabled' => false } } }
    ['_pages/blog.md', '_includes/related_posts.liquid'].each do |path|
      html = Nokogiri::HTML.fragment(render_file(path, payload))
      assert_empty html.css('img, [onerror], [onload]'), path
      assert_includes html.text, doc.data['title']
    end
  end

  def test_local_author_html_and_normal_imported_links_remain_usable
    local = Jekyll::Document.new(@site.in_source_dir('_posts/2025-01-02-local.md'), site: @site, collection: @site.posts)
    local.data['title'] = '<em>Local research</em>'
    local.data['date'] = Time.utc(2025, 1, 2)
    local.data['redirect'] = local.url
    html = Nokogiri::HTML.fragment(render_file('_includes/latest_posts.liquid', {
      'site' => { 'posts' => [local.to_liquid] }, 'page' => { 'latest_posts' => { 'limit' => 6 } } }))
    assert_equal 'Local research', html.at_css('a em').text
    assert_equal local.url, html.at_css('a')['href']
    doc = import
    html = Nokogiri::HTML.fragment(Jekyll::Renderer.new(@site, doc).run)
    assert_equal 'Useful', html.at_css('strong').text
    assert_equal 'https://example.org/paper', html.at_css('a')['href']
    assert_equal 'Research & results', doc.data['title']
  end

  def test_invalid_navigation_is_rejected_and_unicode_https_is_preserved
    ['javascript:alert(1)', 'data:text/html,test', '//evil.example/x', "https://example.org/\nfoo", 'https://example.org\\evil', 'https://user:password@example.org', ''].each do |url|
      @site.posts.docs.clear
      import(url: url)
      assert_empty @site.posts.docs, url.inspect
    end
    doc = import(url: 'https://example.org/연구?q=논문')
    assert_match(%r{\Ahttps://example.org/}, doc.data['redirect'])
    assert_includes doc.data['redirect'], '%'
  end

  def test_body_is_sanitized_after_markdown_and_liquid_is_not_executed
    doc = import(body: "**Useful**\n\n<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[bad](javascript:alert)\n\n{{ site.secret }}")
    output = Jekyll::Renderer.new(@site, doc).run
    html = Nokogiri::HTML.fragment(output)
    assert_empty html.css('script, [onerror], a[href^="javascript:"]')
    assert_equal 'Useful', html.at_css('strong').text
    assert_includes html.text, '{{ site.secret }}'
    assert_equal '/blog/2025/research-results/', doc.url
  end

  def test_search_serializes_all_post_strings_and_navigation_round_trips
    attack = 'https://example.org/");},injected:(globalThis.compromised=1),handler:()=>{window.open("'
    # Exercise the output boundary independently of importer validation too.
    ['Research', "Quoted title" + 34.chr + 10.chr + 92.chr].each do |title|
      post = { 'title' => title, 'description' => title, 'redirect' => attack }
      script = render_file('_scripts/search.liquid.js', { 'site' => {
        'posts_in_search' => true, 'posts' => [post], 'pages' => [], 'collections' => [] } })
      runner = <<~JS
        const vm = require('node:vm');
        let input = '';
        process.stdin.on('data', chunk => input += chunk);
        process.stdin.on('end', () => {
          const ninja = {};
          const context = { document: { querySelector: () => ninja }, window: { open: u => context.opened = u } };
          vm.runInNewContext(input, context, { timeout: 1000 });
          ninja.data.find(x => x.section === 'Posts').handler();
          process.stdout.write(JSON.stringify({ compromised: context.compromised || false, opened: context.opened }));
        });
      JS
      stdout, stderr, status = Open3.capture3(ENV.fetch('NODE', 'node'), '-e', runner, stdin_data: script)
      assert status.success?, stderr
      result = JSON.parse(stdout)
      assert_equal false, result['compromised']
      assert_equal attack, result['opened']
    end
  end

  def test_metadata_json_ld_handles_quotes_and_script_terminators
    doc = import(title: 'A \\ title </script><img src=x onerror=alert(1)>', summary: "Quote \" and newline\n")
    html = Nokogiri::HTML.fragment(render_file('_includes/metadata.liquid', {
      'page' => doc.to_liquid, 'site' => { 'serve_schema_org' => true, 'title' => 'Research', 'url' => 'https://example.org' } }))
    assert_empty html.css('img, [onerror]')
    scripts = html.css('script[type="application/ld+json"]')
    assert_equal 1, scripts.length
    data = JSON.parse(scripts.first.content)
    assert_equal doc.data['title'], data['headline']
  end
end
