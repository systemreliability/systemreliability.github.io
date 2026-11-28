require "minitest/autorun"
require "jekyll"
require "yaml"
require_relative "../_plugins/google-scholar-citations"

class ScholarProfileTest < Minitest::Test
  def test_yaml_feeds_existing_tag_and_publication_badge
    data = YAML.load_file(File.expand_path("../_data/citations.yml", __dir__))
    @site = Struct.new(:data).new({ "citations" => data })
    key, paper = data.fetch("papers").find { |_, entry| entry.fetch("citations").between?(1, 99) }
    expected = paper.fetch("citations").to_s
    template = Liquid::Template.parse("{% google_scholar_citations author article %}")
    assert_equal expected, template.render!({ "author" => "cLfMY9wAAAAJ", "article" => key.split(":").last }, registers: { site: @site })
    # Use the existing badge's data lookup unchanged.
    layout = File.read(File.expand_path("../_layouts/bib.liquid", __dir__))
    fragment = layout.split("{% assign citation_count = 0 %}", 2).last.split("<img", 2).first
    rendered = Liquid::Template.parse("{% assign citation_count = 0 %}" + fragment + "{{ citation_count }}").render!(
      "site" => { "scholar_userid" => "cLfMY9wAAAAJ", "data" => @site.data },
      "entry" => { "google_scholar_id" => key.split(":").last }
    )
    assert_equal expected, rendered.strip
  end
end
