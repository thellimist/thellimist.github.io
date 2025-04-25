module Jekyll
  module ReadingTimeFilter
    def reading_time(input)
      # Remove front matter
      text = input.to_s.gsub(/---\s*[\s\S]*?---\s*/, '')
      
      # Remove HTML tags
      text = text.gsub(/<[^>]*>/, '')
      
      # Remove extra whitespace
      text = text.gsub(/\s+/, ' ').strip
      
      # Simple word count
      words = text.split(/\s+/).reject(&:empty?)
      minutes = (words.size / 200.0).ceil # 200 words per minute
      minutes = 1 if minutes < 1 # Minimum 1 minute
      
      "#{minutes} min read"
    end
  end
end

Liquid::Template.register_filter(Jekyll::ReadingTimeFilter) 