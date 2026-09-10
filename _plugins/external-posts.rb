require 'feedjira'
require 'httparty'
require 'jekyll'
require 'nokogiri'
require 'time'
require 'cgi'
require 'addressable/uri'
require 'loofah'

module ExternalPosts
  module HtmlFilters
    # Keep stored metadata as text for feeds/JSON; escape at HTML consumers.
    def external_post_escape(value, external_source)
      external_source.to_s.empty? ? value : CGI.escapeHTML(value.to_s)
    end
  end

  class ExternalPostsGenerator < Jekyll::Generator
    safe true
    priority :high

    def generate(site)
      if site.config['external_sources'] != nil
        site.config['external_sources'].each do |src|
          puts "Fetching external posts from #{src['name']}:"
          if src['rss_url']
            fetch_from_rss(site, src)
          elsif src['posts']
            fetch_from_urls(site, src)
          end
        end
      end
    end

    def fetch_from_rss(site, src)
      xml = HTTParty.get(src['rss_url']).body
      return if xml.nil?
      feed = Feedjira.parse(xml)
      process_entries(site, src, feed.entries)
    end

    def process_entries(site, src, entries)
      entries.each do |e|
        puts "...fetching #{e.url}"
        create_document(site, src['name'], e.url, {
          title: e.title,
          content: e.content,
          summary: e.summary,
          published: e.published
        })
      end
    end

    def create_document(site, source_name, url, content)
      # A feed may link elsewhere, but it must not supply executable navigation.
      begin
        raise ArgumentError if url.to_s.match?(/[\x00-\x20\x7f\\]/)
        parsed_url = Addressable::URI.parse(url.to_s).normalize
        unless %w[http https].include?(parsed_url.scheme) && !parsed_url.host.to_s.empty? && parsed_url.userinfo.nil?
          raise ArgumentError
        end
        url = parsed_url.to_s
      rescue Addressable::URI::InvalidURIError, ArgumentError
        Jekyll.logger.warn 'External posts:', 'Skipping an entry with an invalid HTTP(S) URL'
        return
      end

      source_name = source_name.to_s.empty? ? 'External' : source_name.to_s
      title = content[:title].to_s

      # check if title is composed only of whitespace or foreign characters
      if title.gsub(/[^\w]/, '').strip.empty?
        # use the source name and last url segment as fallback
        slug = "#{source_name.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')}-#{url.split('/').last}"
      else
        # parse title from the post or use the source name and last url segment as fallback
        slug = title.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')
        slug = "#{source_name.downcase.strip.gsub(' ', '-').gsub(/[^\w-]/, '')}-#{url.split('/').last}" if slug.empty?
      end

      # Convert once, then sanitize. An HTML document avoids a second Markdown
      # pass turning text into active markup after sanitization.
      converter = site.find_converter_instance(::Jekyll::Converters::Markdown)
      body = Loofah.fragment(converter.convert(content[:content].to_s)).scrub!(:prune).to_s
      path = site.in_source_dir("_posts/#{slug}.html")
      doc = Jekyll::Document.new(
        path, { :site => site, :collection => site.collections['posts'] }
      )
      doc.data['external_source'] = CGI.escapeHTML(source_name.to_s)
      doc.data['title'] = title
      doc.data['feed_content'] = body
      doc.data['description'] = content[:summary].to_s
      doc.data['date'] = content[:published]
      doc.data['redirect'] = url
      doc.data['render_with_liquid'] = false
      doc.content = body
      site.collections['posts'].docs << doc
    end

    def fetch_from_urls(site, src)
      src['posts'].each do |post|
        puts "...fetching #{post['url']}"
        content = fetch_content_from_url(post['url'])
        content[:published] = parse_published_date(post['published_date'])
        create_document(site, src['name'], post['url'], content)
      end
    end

    def parse_published_date(published_date)
      case published_date
      when String
        Time.parse(published_date).utc
      when Date
        published_date.to_time.utc
      else
        raise "Invalid date format for #{published_date}"
      end
    end

    def fetch_content_from_url(url)
      html = HTTParty.get(url).body
      parsed_html = Nokogiri::HTML(html)

      title = parsed_html.at('head title')&.text.strip || ''
      description = parsed_html.at('head meta[name="description"]')&.attr('content')
      description ||= parsed_html.at('head meta[name="og:description"]')&.attr('content')
      description ||= parsed_html.at('head meta[property="og:description"]')&.attr('content')

      body_content = parsed_html.search('p').map { |e| e.text }
      body_content = body_content.join() || ''

      {
        title: title,
        content: body_content,
        summary: description
        # Note: The published date is now added in the fetch_from_urls method.
      }
    end

  end
end

Liquid::Template.register_filter(ExternalPosts::HtmlFilters)
