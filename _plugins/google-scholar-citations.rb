require "active_support/all"

# Keep legacy Liquid tag callers compatible, with no network access.
module Jekyll
  class GoogleScholarCitationsTag < Liquid::Tag
    include ActiveSupport::NumberHelper

    def initialize(tag_name, params, tokens)
      super
      @scholar_id, @article_id = params.split
    end

    def render(context)
      return "N/A" unless @scholar_id && @article_id

      scholar_id = context[@scholar_id]
      article_id = context[@article_id]
      data = context.registers[:site].data.fetch("citations", {})
      papers = data.fetch("papers", {})
      paper = papers["#{scholar_id}:#{article_id}"] || papers[article_id]
      return "N/A" unless paper && paper["citations"].is_a?(Integer)

      number_to_human(paper["citations"], format: "%n%u", precision: 2,
                     units: { thousand: "K", million: "M", billion: "B" })
    end
  end
end

Liquid::Template.register_tag("google_scholar_citations", Jekyll::GoogleScholarCitationsTag)
