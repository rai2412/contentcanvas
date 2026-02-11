// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    handleRouting();
    
    // Listen for hash changes
    window.addEventListener('hashchange', handleRouting);
});

// Handle routing based on hash
function handleRouting() {
    const hash = window.location.hash.slice(1) || 'home';
    
    if (hash === 'home') {
        showHome();
    } else {
        loadMarkdownPage(hash);
    }
}

// Show home page
function showHome() {
    document.getElementById('home-content').classList.remove('page-hidden');
    document.getElementById('home-content').classList.add('page-active');
    document.getElementById('dynamic-content').innerHTML = '';
    document.getElementById('dynamic-content').classList.add('page-hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Load markdown page
async function loadMarkdownPage(pageName) {
    const homeContent = document.getElementById('home-content');
    const dynamicContent = document.getElementById('dynamic-content');
    
    // Hide home, show dynamic content area
    homeContent.classList.remove('page-active');
    homeContent.classList.add('page-hidden');
    dynamicContent.classList.remove('page-hidden');
    
    try {
        // Fetch the markdown file
        const response = await fetch(`${pageName}.md`);
        if (!response.ok) {
            throw new Error(`Failed to load ${pageName}.md`);
        }
        
        const markdownText = await response.text();
        
        // Convert markdown to HTML using marked.js
        const htmlContent = marked.parse(markdownText);
        
        // Wrap content in container with back link
        const wrappedContent = `
            <div class="container">
                <a href="#home" class="back-link">← Back to home</a>
                ${htmlContent}
            </div>
        `;
        
        dynamicContent.innerHTML = wrappedContent;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error loading page:', error);
        dynamicContent.innerHTML = `
            <div class="container">
                <a href="#home" class="back-link">← Back to home</a>
                <h1>Page Not Found</h1>
                <p>Sorry, the page you're looking for doesn't exist.</p>
            </div>
        `;
    }
}

// Scroll to a specific section (for in-page navigation)
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Configure marked.js options for better rendering
if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: true,
        mangle: false
    });
}