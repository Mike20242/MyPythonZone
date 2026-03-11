from flask import Flask, render_template

app = Flask(__name__)

# Mock database of blog posts
posts = [
    {
        'id': 1,
        'title': 'The Future of AI and Machine Learning',
        'author': 'Jane Doe',
        'date': 'March 10, 2026',
        'summary': 'A brief look into how AI is shaping the future of software development.',
        'content': '''
            <p>Artificial Intelligence has evolved from standard machine learning algorithms to complex models capable of incredible feats. We are seeing breakthroughs across the board, from natural language processing to computer vision.</p>
            <h3>What's Next?</h3>
            <p>The next decade will likely be defined by the integration of AI into every facet of our daily lives, making it essential for developers to understand the basics of AI integration and model tuning.</p>
            <p>Flask makes it incredibly easy to expose AI models via APIs or visually appealing web dashboards.</p>
        '''
    },
    {
        'id': 2,
        'title': 'Why Flask remains relevant in 2026',
        'author': 'John Smith',
        'date': 'March 11, 2026',
        'summary': 'Exploring why you should still learn and use Flask today for rapid development.',
        'content': '''
            <p>With so many web frameworks available, why do developers still choose Flask? The answer lies in its simplicity and flexibility.</p>
            <p>Flask provides the bare minimum, which means you have the ultimate control over how you want to structure your application.</p>
            <h3>Great for Microservices</h3>
            <p>In a microservices architecture, Flask shines by allowing developers to spin up specific services without unnecessary boilerplate.</p>
        '''
    },
    {
        'id': 3,
        'title': 'Design Aesthetics for Web Apps',
        'author': 'Alex Taylor',
        'date': 'March 12, 2026',
        'summary': 'Tips and tricks for making your sites pop using Vanilla CSS and modern design.',
        'content': '''
            <p>Building beautiful UIs with Vanilla CSS is an art. By utilizing CSS variables, Flexbox, and Grid, you can achieve any layout imaginable without relying on heavy frameworks.</p>
            <h3>The Power of Dark Mode</h3>
            <p>A well-implemented dark theme with sleek colors and glassmorphism can elevate your application and provide a premium feel.</p>
        '''
    }
]

@app.route('/')
def home():
    # Show the two most recent posts on the home page
    return render_template('blog_home.html', posts=posts[:2])

@app.route('/blog')
def blog_list():
    return render_template('blog_list.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_detail(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if post is None:
        return render_template('blog_404.html'), 404
    return render_template('blog_detail.html', post=post)

@app.route('/about')
def about():
    return render_template('blog_about.html')

@app.route('/contact')
def contact():
    return render_template('blog_contact.html')

if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with Exercise 5.4 running on port 5000
    app.run(debug=True, port=5001)
