require "minitest/autorun"
require "jekyll"
require "yaml"
require_relative "../_plugins/scholar-profile-data"
require_relative "../_plugins/google-scholar-citations"

class ScholarProfileTest < Minitest::Test
  def setup
    @legacy = YAML.load_file(File.expand_path("../_data/citations.yml", __dir__))
    @site = Struct.new(:data).new({ "citations" => @legacy })
  end

  def test_no_snapshot_preserves_existing_data
    ScholarProfileData.apply(@site)
    assert_same @legacy, @site.data["citations"]
  end

  def test_snapshot_uses_same_keys_and_keeps_unobserved_papers
    key = @legacy["papers"].keys.first
    @site.data["scholar_profile"] = {
      "metadata" => { "last_updated" => "2026-11-27 09:10:00", "fetch_status" => "success" },
      "profile" => { "user_id" => "cLfMY9wAAAAJ" },
      "papers" => { key => @legacy["papers"][key].merge("citations" => 99) }
    }
    ScholarProfileData.apply(@site)
    assert_equal @legacy["papers"].keys.sort, @site.data["citations"]["papers"].keys.sort
    assert_equal 99, @site.data["citations"]["papers"][key]["citations"]
    template = Liquid::Template.parse("{% google_scholar_citations author article %}")
    assert_equal "99", template.render!({ "author" => "cLfMY9wAAAAJ", "article" => key.split(":").last }, registers: { site: @site })
    # Use the existing badge's data lookup unchanged.
    layout = File.read(File.expand_path("../_layouts/bib.liquid", __dir__))
    fragment = layout.split("{% assign citation_count = 0 %}", 2).last.split("<img", 2).first
    rendered = Liquid::Template.parse("{% assign citation_count = 0 %}" + fragment + "{{ citation_count }}").render!(
      "site" => { "scholar_userid" => "cLfMY9wAAAAJ", "data" => @site.data },
      "entry" => { "google_scholar_id" => key.split(":").last }
    )
    assert_equal "99", rendered.strip
  end

  def test_corrupt_snapshot_fails_without_replacing_legacy
    @site.data["scholar_profile"] = { "papers" => {} }
    assert_raises(RuntimeError) { ScholarProfileData.apply(@site) }
    assert_same @legacy, @site.data["citations"]
  end
end
