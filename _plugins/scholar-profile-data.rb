# Jekyll loads _data/*.json natively. Preserve the existing Liquid data interface
# and the last YAML snapshot until a fully validated local collection exists.
module ScholarProfileData
  def self.apply(site)
    snapshot = site.data["scholar_profile"]
    return unless snapshot

    valid = snapshot.is_a?(Hash) &&
      snapshot.dig("metadata", "fetch_status") == "success" &&
      snapshot.dig("profile", "user_id") == "cLfMY9wAAAAJ" &&
      snapshot["papers"].is_a?(Hash) && !snapshot["papers"].empty? &&
      snapshot["papers"].all? do |key, paper|
        key.is_a?(String) && paper.is_a?(Hash) &&
          paper["citations"].is_a?(Integer) && paper["citations"] >= 0
      end
    raise "Invalid local Scholar snapshot; refusing to replace citation data" unless valid

    legacy = site.data.fetch("citations", {})
    site.data["citations"] = legacy.merge(snapshot)
    site.data["citations"]["papers"] = legacy.fetch("papers", {}).merge(snapshot["papers"])
  end
end

Jekyll::Hooks.register :site, :post_read do |site|
  ScholarProfileData.apply(site)
end
