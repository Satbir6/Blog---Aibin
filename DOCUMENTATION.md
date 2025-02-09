# Aibin Blog Platform - Technical Documentation

## 1. Project Overview

### Purpose and Core Functionality
A modern, feature-rich blogging platform built with Flask that enables content creation, moderation, and user interaction. The platform supports multiple user roles, content categorization, and real-time features.

### Target Audience
- Content Creators: Writers and bloggers who want to publish articles
- Readers: Users who consume and interact with content
- Moderators/Admins: Users who manage content and user permissions

### Key Features
- 🔐 User Authentication & Authorization
- 📝 Rich Text Blog Creation/Editing
- 🏷️ Category Management
- 👍 Like & Comment System
- 🔍 Full-Text Search
- 👮 Content Moderation System
- 📱 Responsive Design
- 🖼️ Image Upload Support
- 🎨 Modern UI with Tailwind CSS

## 2. Technology Stack

### Backend
- **Framework**: Flask 3.1.0
  - *Why*: Lightweight, flexible, and perfect for medium-sized applications
- **Extensions**:
  - Flask-SQLAlchemy 3.1.1: ORM for database operations
  - Flask-Login 0.6.3: User session management
  - Flask-WTF 1.2.2: Form handling and CSRF protection
  - Flask-Migrate 4.1.0: Database migrations
  - Flask-Bcrypt 1.0.1: Password hashing
  - Flask-CKEditor 1.0.0: Rich text editing

### Frontend
- **Template Engine**: Jinja2 3.1.5
- **CSS Framework**: Tailwind CSS
- **JavaScript**: Vanilla JS with some Alpine.js
- **Rich Text Editor**: CKEditor
- **Icons**: Heroicons

### Database
- **System**: SQLite (Development) / PostgreSQL (Production)
- **ORM**: SQLAlchemy 2.0.37
- **Migration Tool**: Alembic via Flask-Migrate

### Development Tools
- **Package Manager**: pip (Python) / npm (Node.js)
- **Version Control**: Git
- **Code Editor**: VS Code recommended
- **API Testing**: Postman

## 3. Project Structure
\`\`\`
project-root/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── tailwind.config.js    # Tailwind CSS configuration
├── static/               # Static assets
│   ├── css/             # Compiled CSS
│   ├── js/              # JavaScript files
│   ├── images/          # Image assets
│   ├── uploads/         # User uploads
│   ├── dist/            # Compiled assets
│   ├── src/             # Source assets
│   └── vendor/          # Third-party assets
├── templates/           # Jinja2 templates
│   ├── admin/          # Admin-specific templates
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── blogs.html      # Blog listing
│   ├── view_blog.html  # Single blog view
│   └── ...             # Other templates
├── instance/           # Instance-specific files
└── Docs/              # Project documentation
\`\`\`

## 4. Python Code Deep Dive

### Core Components

#### Models
1. **User Model**
   - Handles user authentication and profile data
   - Supports admin/regular user roles
   - Manages user relationships (comments, likes)

2. **Blog Model**
   - Core content model with moderation support
   - Supports draft/published states
   - Handles relationships with categories, comments, likes

3. **Category Model**
   - Organizes blogs into topics
   - Supports hierarchical categorization

4. **Comment & Like Models**
   - Handle user interactions
   - Track engagement metrics

### Key Workflows

#### Authentication Flow
\`\`\`python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
\`\`\`

#### Blog Creation/Moderation Flow
\`\`\`python
@app.route('/create-blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == 'POST':
        blog = Blog(
            title=request.form.get('title'),
            content=request.form.get('content'),
            author=current_user,
            category_id=request.form.get('category_id')
        )
        db.session.add(blog)
        db.session.commit()
\`\`\`

## 5. Database Schema

### Entity Relationship Diagram
\`\`\`mermaid
erDiagram
    User ||--o{ Blog : writes
    User ||--o{ Comment : makes
    User ||--o{ Like : gives
    Blog ||--o{ Comment : has
    Blog ||--o{ Like : receives
    Blog }|--|| Category : belongs_to
    Blog }|--|| User : moderated_by

    User {
        int id PK
        string name
        string email
        string password
        boolean is_admin
        datetime created_at
        datetime updated_at
    }

    Blog {
        int id PK
        string title
        text content
        int author_id FK
        int category_id FK
        string status
        string moderation_status
        text moderation_comment
        int moderated_by FK
        datetime moderated_at
        datetime created_at
        datetime updated_at
    }

    Category {
        int id PK
        string name
        text description
        datetime created_at
        datetime updated_at
    }

    Comment {
        int id PK
        text content
        int blog_id FK
        int user_id FK
        datetime created_at
        datetime updated_at
    }

    Like {
        int id PK
        int blog_id FK
        int user_id FK
        datetime created_at
    }
\`\`\`

### Key Relationships
- One-to-Many:
  - User → Blogs (author)
  - User → Comments
  - Blog → Comments
  - Category → Blogs
- Many-to-One:
  - Blog → User (moderator)
  - Blog → Category

## 6. Frontend Architecture

### Template Hierarchy
- `base.html`: Base template with common layout
  - Navigation
  - User menu
  - Flash messages
  - Footer
- Content templates extend base.html:
  - `index.html`: Homepage
  - `blogs.html`: Blog listing
  - `view_blog.html`: Single blog view
  - etc.

### Key Components
1. **Navigation**
   - Responsive menu
   - User authentication state
   - Search bar

2. **Blog Cards**
   - Title, excerpt, metadata
   - Category tags
   - Like/comment counters

3. **Rich Text Editor**
   - CKEditor integration
   - Image upload support
   - Markdown support

## 7. API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/search-suggestions` | GET | Get search suggestions | No |
| `/api/blogs` | GET | List all blogs | No |
| `/api/blog/<id>` | GET | Get single blog | No |
| `/api/blog` | POST | Create blog | Yes |
| `/api/blog/<id>` | PUT | Update blog | Yes |
| `/api/blog/<id>` | DELETE | Delete blog | Yes |
| `/api/like/<id>` | POST | Like/unlike blog | Yes |
| `/api/moderate/<id>` | POST | Moderate blog | Yes (Admin) |

## 8. Deployment & Configuration

### Environment Setup
1. Python 3.8+ required
2. Create virtual environment:
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate   # Windows
   \`\`\`
3. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   npm install
   \`\`\`

### Configuration
Key environment variables:
- `FLASK_ENV`: development/production
- `SECRET_KEY`: App secret key
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: Path for file uploads

### Production Deployment
1. Set up PostgreSQL database
2. Configure Gunicorn
3. Set up Nginx reverse proxy
4. Enable SSL with Let's Encrypt
5. Configure static file serving

## 9. Testing & Validation

### Input Validation
- Form validation using WTForms
- Content sanitization using Bleach
- File upload validation

### Security Measures
- CSRF protection
- Password hashing
- SQL injection prevention
- XSS protection

## 10. Future Scope

### Planned Features
- 🔄 RSS Feed Support
- 📊 Analytics Dashboard
- 📱 Progressive Web App
- 🌐 Multi-language Support
- 🔔 Email Notifications
- 📝 API Documentation

### Scalability Improvements
- Redis caching
- CDN integration
- Elasticsearch for search
- Celery for background tasks

## 11. Conclusion

The Aibin Blog Platform provides a robust foundation for content creation and management. Its modular architecture allows for easy extension and maintenance, while the modern tech stack ensures good performance and developer experience.

## 12. Appendices

### Glossary
- **ORM**: Object-Relational Mapping
- **CSRF**: Cross-Site Request Forgery
- **XSS**: Cross-Site Scripting
- **JWT**: JSON Web Token

### References
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [CKEditor Documentation](https://ckeditor.com/docs/) 