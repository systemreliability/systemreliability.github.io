module Jekyll
  module HideCustomBibtex
    def hideCustomBibtex(input)
      keywords = Array(@context.registers[:site].config['filtered_bibtex_keywords'])
      keywords |= ['openalex_id']

      keywords.each do |keyword|
        input = input.gsub(/^.*\b#{keyword}\b *= *\{.*$\n/, '')
      end

      # Clean superscripts in author lists
      input = input.gsub(/^.*\bauthor\b *= *\{.*$\n/) { |line| line.gsub(/[*†‡§¶‖&^]/, '') }

      return input
    end
  end
end

Liquid::Template.register_filter(Jekyll::HideCustomBibtex)
