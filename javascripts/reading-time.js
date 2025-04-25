// Calculate reading time based on word count
// Average reading speed is 200-250 words per minute
function calculateReadingTime() {
  // Helper function to get accurate word count
  function getWordCount(text) {
    // Remove code blocks, images, and other non-content elements
    text = text.replace(/```[\s\S]*?```/g, ''); // Remove code blocks
    text = text.replace(/!\[.*?\]\(.*?\)/g, ''); // Remove images
    text = text.replace(/\[.*?\]\(.*?\)/g, ''); // Remove links
    text = text.replace(/<[^>]*>/g, ''); // Remove HTML tags
    text = text.replace(/\s+/g, ' ').trim(); // Normalize whitespace
    
    // Count words (more accurate method)
    const words = text.split(/\s+/).filter(word => word.length > 0);
    console.log('Word count:', words.length, 'Text:', text.substring(0, 100) + '...');
    return words.length;
  }

  // Handle post cards in the blog index
  const postCards = document.querySelectorAll('.post-card');
  postCards.forEach(card => {
    const title = card.querySelector('.post-card-title');
    const meta = card.querySelector('.post-card-meta');
    if (!title || !meta) return;
    
    // Get the post URL to fetch the content
    const postUrl = card.querySelector('a').getAttribute('href');
    if (!postUrl) return;

    // Skip external URLs (like Medium posts)
    if (postUrl.startsWith('http') && !postUrl.includes(window.location.hostname)) {
      return;
    }
    
    // Fetch the post content
    fetch(postUrl)
      .then(response => response.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const content = doc.querySelector('.post-content');
        if (!content) return;
        
        const text = content.textContent;
        const wordCount = getWordCount(text);
        // More conservative estimate: 150 words per minute
        const readingTime = Math.max(1, Math.ceil(wordCount / 150));
        
        const readingTimeElement = document.createElement('div');
        readingTimeElement.className = 'post-reading-time';
        readingTimeElement.textContent = `${readingTime} min read`;
        
        meta.appendChild(readingTimeElement);
      })
      .catch(error => console.error('Error fetching post content:', error));
  });

  // Handle full post content
  const postContent = document.querySelector('.post-content');
  if (postContent) {
    const text = postContent.textContent;
    const wordCount = getWordCount(text);
    // More conservative estimate: 150 words per minute
    const readingTime = Math.max(1, Math.ceil(wordCount / 150));
    
    const readingTimeElement = document.createElement('div');
    readingTimeElement.className = 'post-reading-time';
    readingTimeElement.textContent = `${readingTime} min read`;
    
    const dateElement = document.querySelector('.post-date');
    if (dateElement) {
      dateElement.parentNode.insertBefore(readingTimeElement, dateElement.nextSibling);
    }
  }
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', calculateReadingTime); 