"""
Flask Blog Application
A modern blogging platform with user authentication, content moderation, and admin features.

Author: Aibin
Version: 1.0.0
Created: 2024
"""

# Standard library imports
import re
from math import ceil
from datetime import datetime, timedelta
from collections import defaultdict

# Third-party imports
from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash, 
    jsonify, 
    abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, 
    UserMixin, 
    login_user, 
    logout_user, 
    login_required, 
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, case
import bleach

# === App Configuration ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['POSTS_PER_PAGE'] = 9

# === Error Handlers ===
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 Not Found errors."""
    return render_template('error.html',
                        user=current_user,
                         error_code='404',
                         error_message='Page Not Found',
                         error_description='The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 Internal Server Error."""
    return render_template('error.html',
                        user=current_user,
                         error_code='500',
                         error_message='Internal Server Error',
                         error_description='Something went wrong on our end. Please try again later.'), 500

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Make POSTS_PER_PAGE available to all templates
@app.context_processor
def utility_processor():
    return {
        'POSTS_PER_PAGE': app.config['POSTS_PER_PAGE'],
        'min': min  # Make min() function available in templates
    }

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))

# === Models ===
class User(UserMixin, db.Model):
    """User model representing blog users and admins.
    
    Attributes:
        id: Primary key
        name: User's full name
        email: User's email address (unique)
        password: Hashed password
        is_admin: Boolean flag for admin status
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def check_password(self, password):
        """Verify if provided password matches stored hash."""
        return check_password_hash(self.password, password)

class Category(db.Model):
    """Category model for organizing blog posts.
    
    Attributes:
        id: Primary key
        name: Category name (unique)
        description: Optional category description
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        blogs: Relationship to associated Blog posts
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    blogs = db.relationship('Blog', backref='category', lazy=True)

class Blog(db.Model):
    """Blog post model with moderation support.
    
    Attributes:
        id: Primary key
        title: Post title
        content: Post content (HTML allowed)
        author_id: Foreign key to User model
        category_id: Foreign key to Category model
        status: Publication status (draft/published)
        moderation_status: Moderation state (pending/approved/rejected)
        moderation_comment: Optional moderator feedback
        moderated_by: Foreign key to moderator User
        moderated_at: Timestamp of last moderation action
        created_at: Post creation timestamp
        updated_at: Last update timestamp
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')
    moderation_status = db.Column(db.String(20), default='pending')
    moderation_comment = db.Column(db.Text)
    moderated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    moderated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('Comment', backref='blog', lazy=True)
    likes = db.relationship('Like', backref='blog', lazy=True)
    author = db.relationship('User', foreign_keys=[author_id], backref='blogs')
    moderator = db.relationship('User', foreign_keys=[moderated_by], backref='moderated_blogs')

class Comment(db.Model):
    """Comment model for blog posts.
    
    Attributes:
        id: Primary key
        content: Comment text
        blog_id: Foreign key to associated Blog
        user_id: Foreign key to commenter User
        created_at: Comment creation timestamp
        updated_at: Last update timestamp
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='comments')

class Like(db.Model):
    """Like model for tracking blog post likes.
    
    Attributes:
        id: Primary key
        blog_id: Foreign key to liked Blog
        user_id: Foreign key to User who liked
        created_at: Timestamp of like action
    """
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# === Authentication Routes ===
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration.
    
    GET: Display signup form
    POST: Create new user account
    """
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already exists', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login.
    
    GET: Display login form
    POST: Authenticate user credentials
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome back!', 'success')
            return redirect(url_for('home'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('login.html',user=current_user)

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('home'))

# === Public Routes ===
@app.route('/')
def home():
    """Render homepage with recent and featured content."""
    # Get recent published blogs
    recent_blogs = Blog.query.filter(
        Blog.status == 'published',
        Blog.moderation_status != 'rejected'
    ).order_by(Blog.created_at.desc())\
        .limit(3).all()
    
    # Get all categories with their blog counts
    categories = Category.query.all()
    for category in categories:
        category.blog_count = len([b for b in category.blogs if b.status == 'published' and b.moderation_status != 'rejected'])
    
    # Get featured blogs (most liked)
    featured_blogs = Blog.query.filter(
        Blog.status == 'published',
        Blog.moderation_status != 'rejected'
    ).join(Like)\
        .group_by(Blog.id)\
        .order_by(db.func.count(Like.id).desc())\
        .limit(3).all()
    
    return render_template('index.html',
                         recent_blogs=recent_blogs,
                         categories=categories,
                         featured_blogs=featured_blogs,
                         user=current_user)

@app.route('/blogs')
def all_blogs():
    """Display all published blogs with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    sort = request.args.get('sort', 'recent')  # 'recent', 'popular'
    
    # Base query
    query = Blog.query.filter(Blog.status == 'published', Blog.moderation_status != 'rejected')
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Apply sorting
    if sort == 'popular':
        query = query.join(Like)\
            .group_by(Blog.id)\
            .order_by(func.count(Like.id).desc())
    else:  # recent
        query = query.order_by(Blog.created_at.desc())
    
    # Pagination
    total_posts = query.count()
    total_pages = ceil(total_posts / app.config['POSTS_PER_PAGE'])
    
    blogs = query.offset((page - 1) * app.config['POSTS_PER_PAGE'])\
        .limit(app.config['POSTS_PER_PAGE']).all()
    
    categories = Category.query.all()
    
    return render_template('blogs.html',
                         blogs=blogs,
                         categories=categories,
                         current_page=page,
                         total_pages=total_pages,
                         current_category=category_id,
                         current_sort=sort,
                         user=current_user)

@app.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
def view_blog(blog_id):
    """Display a single blog post and handle comments.
    
    GET: Show blog post, comments, and related content
    POST: Add a new comment (authenticated users only)
    """
    blog = Blog.query.get_or_404(blog_id)
    # Prevent access to rejected blogs for non-admin users
    if (blog.status == 'rejected' or blog.moderation_status == 'rejected') and \
       (not current_user.is_authenticated or not current_user.is_admin):
        abort(404)
    
    has_liked = False
    if current_user.is_authenticated:
        has_liked = any(like.user_id == current_user.id for like in blog.likes)
    
    # Handle comment submission
    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form.get('comment')
        if content:
            comment = Comment(
                content=content,
                blog_id=blog.id,
                user_id=current_user.id
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('view_blog', blog_id=blog.id))
    
    # Get comments and related content
    comments = Comment.query.filter_by(blog_id=blog.id)\
        .order_by(Comment.created_at.desc()).all()
    
    related_blogs = Blog.query.filter(
        Blog.category_id == blog.category_id,
        Blog.id != blog.id,
        Blog.status == 'published'
    ).limit(3).all()
    
    return render_template('view_blog.html', 
                         blog=blog, 
                         comments=comments, 
                         related_blogs=related_blogs,
                         has_liked=has_liked,
                         user=current_user)

@app.route('/category/<int:category_id>')
def category_view(category_id):
    """Display blogs from a specific category."""
    page = request.args.get('page', 1, type=int)
    category = Category.query.get_or_404(category_id)
    
    query = Blog.query.filter_by(category_id=category_id, status='published')\
        .order_by(Blog.created_at.desc())
    
    total_posts = query.count()
    total_pages = ceil(total_posts / app.config['POSTS_PER_PAGE'])
    
    blogs = query.offset((page - 1) * app.config['POSTS_PER_PAGE'])\
        .limit(app.config['POSTS_PER_PAGE']).all()
    
    return render_template('category.html',
                         category=category,
                         blogs=blogs,
                         current_page=page,
                         total_pages=total_pages,
                         user=current_user)

@app.route('/search')
def search():
    """Search blogs with filtering and pagination."""
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'relevant')  # relevant, newest, most_liked
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return redirect(url_for('home'))
    
    # Base search query
    search_query = Blog.query.filter(
        db.or_(
            Blog.title.ilike(f'%{query}%'),
            Blog.content.ilike(f'%{query}%')
        ),
        Blog.status == 'published',
        Blog.moderation_status!='rejected'
    )
    
    # Apply filters and sorting
    if category_id:
        search_query = search_query.filter_by(category_id=category_id)
    
    if sort_by == 'newest':
        search_query = search_query.order_by(Blog.created_at.desc())
    elif sort_by == 'most_liked':
        search_query = search_query.outerjoin(Like)\
            .group_by(Blog.id)\
            .order_by(func.count(Like.id).desc())
    else:  # relevant - prioritize title matches
        search_query = search_query.order_by(
            db.case((Blog.title.ilike(f'%{query}%'), 1), else_=2),
            Blog.created_at.desc()
        )
    
    # Pagination
    total_results = search_query.count()
    total_pages = ceil(total_results / app.config['POSTS_PER_PAGE'])
    
    showing_from = ((page - 1) * app.config['POSTS_PER_PAGE']) + 1
    showing_to = min(page * app.config['POSTS_PER_PAGE'], total_results)
    
    blogs = search_query.offset((page - 1) * app.config['POSTS_PER_PAGE'])\
        .limit(app.config['POSTS_PER_PAGE']).all()
    
    categories = Category.query.all()
    
    return render_template('search.html',
                         blogs=blogs,
                         categories=categories,
                         query=query,
                         current_category=category_id,
                         current_sort=sort_by,
                         current_page=page,
                         total_pages=total_pages,
                         total_results=total_results,
                         showing_from=showing_from,
                         showing_to=showing_to,
                         highlight_text=highlight_text,
                         user=current_user)

# === User Routes ===
@app.route('/profile')
@login_required
def profile():
    """Display user profile and blog statistics."""
    user_blogs = Blog.query.filter_by(author_id=current_user.id)\
        .order_by(Blog.created_at.desc()).all()
    published_count = sum(1 for blog in user_blogs if blog.status == 'published')
    draft_count = sum(1 for blog in user_blogs if blog.status == 'draft')
    
    return render_template('profile.html', 
                         user=current_user,
                         blogs=user_blogs,
                         published_count=published_count,
                         draft_count=draft_count,
                         )

@app.route('/my-blogs')
@login_required
def my_blogs():
    """Display user's blogs with filtering and sorting."""
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'newest')
    
    # Base query
    query = Blog.query.filter_by(author_id=current_user.id)
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Blog.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Blog.created_at.asc())
    elif sort_by == 'most_liked':
        query = query.outerjoin(Like)\
            .group_by(Blog.id)\
            .order_by(func.count(Like.id).desc())
    elif sort_by == 'most_commented':
        query = query.outerjoin(Comment)\
            .group_by(Blog.id)\
            .order_by(func.count(Comment.id).desc())
    
    blogs = query.all()
    
    return render_template('my_blogs.html', 
                         blogs=blogs,
                         current_status=status_filter,
                         current_sort=sort_by,
                         user=current_user)

@app.route('/create-blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    """Create a new blog post.
    
    GET: Display blog creation form
    POST: Save new blog post
    """
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category')
        status = request.form.get('status', 'draft')
        
        # Sanitize content
        clean_content = bleach.clean(content, 
            tags=['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a'],
            attributes={'a': ['href']})
        
        blog = Blog(
            title=title,
            content=clean_content,
            author_id=current_user.id,
            category_id=category_id,
            status=status
        )
        
        db.session.add(blog)
        db.session.commit()
        
        return redirect(url_for('view_blog', blog_id=blog.id))
    
    return render_template('create_blog.html', categories=categories,
    user=current_user)

@app.route('/edit-blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    """Edit an existing blog post.
    
    GET: Display blog edit form
    POST: Save blog changes
    """
    blog = Blog.query.get_or_404(blog_id)
    if blog.author_id != current_user.id:
        flash('You cannot edit this blog')
        return redirect(url_for('home'))
    
    categories = Category.query.all()
    
    if request.method == 'POST':
        blog.title = request.form.get('title')
        blog.content = bleach.clean(request.form.get('content'),
            tags=['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a'],
            attributes={'a': ['href']})
        blog.category_id = request.form.get('category')
        blog.status = request.form.get('status', 'draft')
        
        db.session.commit()
        return redirect(url_for('view_blog', blog_id=blog.id))
    
    return render_template('edit_blog.html', blog=blog, categories=categories, user=current_user)

@app.route('/delete-blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    """Delete a blog post."""
    blog = Blog.query.get_or_404(blog_id)
    if blog.author_id != current_user.id:
        flash('You are not authorized to delete this post.', 'error')
        return redirect(url_for('home'))
    
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post deleted successfully.', 'success')
    return redirect(url_for('my_blogs'))

@app.route('/like/<int:blog_id>', methods=['POST'])
@login_required
def like_blog(blog_id):
    """Toggle like status for a blog post."""
    blog = Blog.query.get_or_404(blog_id)
    existing_like = Like.query.filter_by(
        user_id=current_user.id,
        blog_id=blog_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        like = Like(user_id=current_user.id, blog_id=blog_id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    return jsonify({
        'action': action,
        'likes_count': len(blog.likes)
    })

# === Admin Routes ===
@app.route('/admin')
@login_required
def admin_dashboard():
    """Display admin dashboard with site statistics."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get date range for charts
    today = datetime.utcnow().date()
    last_30_days = today - timedelta(days=30)
    
    # Daily posts for the last 30 days
    daily_posts = defaultdict(int)
    posts_by_date = db.session.query(
        Blog.created_at,
        func.count(Blog.id).label('count')
    ).filter(Blog.created_at >= last_30_days)\
     .group_by(func.date(Blog.created_at))\
     .all()
    
    for date in (last_30_days + timedelta(days=x) for x in range(31)):
        daily_posts[date.strftime('%Y-%m-%d')] = 0
    for result in posts_by_date:
        date_str = result.created_at.date().strftime('%Y-%m-%d')
        daily_posts[date_str] = result.count
    
    # Posts by category
    category_stats = db.session.query(
        Category.name,
        func.count(Blog.id).label('total_posts'),
        func.sum(case((Blog.status == 'published', 1), else_=0)).label('published_posts')
    ).join(Blog)\
     .group_by(Category.id)\
     .all()
    
    category_stats = [
        {
            'name': stat.name,
            'total_posts': stat.total_posts,
            'published_posts': stat.published_posts,
            'draft_posts': stat.total_posts - stat.published_posts
        }
        for stat in category_stats
    ]
    
    # Gather statistics
    stats = {
        'total_users': User.query.count(),
        'total_posts': Blog.query.count(),
        'total_categories': Category.query.count(),
        'pending_moderation': Blog.query.filter_by(moderation_status='pending').count(),
        'posts_today': Blog.query.filter(
            Blog.created_at >= datetime.utcnow().date()
        ).count(),
        'active_users': User.query.join(Blog, User.id == Blog.author_id).group_by(User.id).count(),
        'popular_categories': db.session.query(
            Category.name,
            func.count(Blog.id).label('post_count')
        ).join(Blog).group_by(Category.id).order_by(
            func.count(Blog.id).desc()
        ).limit(5).all(),
        'daily_posts': daily_posts,
        'category_stats': category_stats
    }
    
    latest_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get recent activity
    recent_activity = []
    
    # Add moderation activity
    recent_moderations = Blog.query.filter(
        Blog.moderation_status.in_(['approved', 'rejected'])
    ).order_by(Blog.moderated_at.desc()).limit(3)
    
    for blog in recent_moderations:
        moderator = User.query.get(blog.moderated_by)
        recent_activity.append({
            'description': f'Blog "{blog.title}" {blog.moderation_status} by {moderator.name}',
            'time': blog.moderated_at.strftime('%B %d, %Y')
        })
    
    # Add new blog posts
    recent_blogs = Blog.query.order_by(Blog.created_at.desc()).limit(3)
    for blog in recent_blogs:
        recent_activity.append({
            'description': f'New blog post: {blog.title} by {blog.author.name}',
            'time': blog.created_at.strftime('%B %d, %Y')
        })
    
    # Sort by time
    recent_activity.sort(key=lambda x: datetime.strptime(x['time'], '%B %d, %Y'), reverse=True)
    recent_activity = recent_activity[:5]  # Keep only the 5 most recent
    
    return render_template('admin_dashboard.html',
                         stats=stats,
                         latest_users=latest_users,
                         recent_activity=recent_activity,
                         user=current_user)

@app.route('/admin/moderate')
@login_required
def moderate_blogs():
    """Display blogs pending moderation."""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    status = request.args.get('status', 'pending')
    blogs = Blog.query.filter_by(moderation_status=status)\
        .order_by(Blog.created_at.desc()).all()
    
    return render_template('admin/moderate_blogs.html', blogs=blogs, current_status=status,
    user=current_user)

@app.route('/admin/moderate/<int:blog_id>', methods=['POST'])
@login_required
def moderate_blog(blog_id):
    """Handle blog moderation actions."""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    blog = Blog.query.get_or_404(blog_id)
    action = request.form.get('action')
    comment = request.form.get('comment', '')
    
    if action not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid action'}), 400
    
    blog.moderation_status = 'approved' if action == 'approve' else 'rejected'
    blog.moderation_comment = comment
    blog.moderated_by = current_user.id
    blog.moderated_at = datetime.utcnow()
    
    # If approved and was published, keep it published
    if action == 'approve' and blog.status == 'published':
        blog.status = 'published'
    else:
        blog.status = 'draft'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Blog {action}d successfully'
    })

# === Category Management Routes ===
@app.route('/categories')
@login_required
def list_categories():
    """Display all blog categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories, user=current_user)

@app.route('/categories/new', methods=['GET', 'POST'])
@login_required
def create_category():
    """Create a new blog category.
    
    GET: Display category creation form
    POST: Save new category
    """
    if not current_user.is_admin:
        flash('Only administrators can manage categories.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if Category.query.filter_by(name=name).first():
            flash('Category already exists')
            return redirect(url_for('create_category'))
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('list_categories'))
    
    return render_template('create_category.html', user=current_user)

@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """Edit an existing category.
    
    GET: Display category edit form
    POST: Save category changes
    """
    if not current_user.is_admin:
        flash('Only administrators can manage categories.', 'error')
        return redirect(url_for('home'))
    
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category and existing_category.id != category_id:
            flash('Category name already exists')
            return redirect(url_for('edit_category', category_id=category_id))
        
        category.name = name
        category.description = description
        db.session.commit()
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('list_categories'))
    
    return render_template('edit_category.html', category=category, user=current_user)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """Delete a category if it has no associated blogs."""
    if not current_user.is_admin:
        flash('Only administrators can manage categories.', 'error')
        return redirect(url_for('home'))
    
    category = Category.query.get_or_404(category_id)
    
    if Blog.query.filter_by(category_id=category_id).first():
        flash('Cannot delete category that has blogs')
        return redirect(url_for('list_categories'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('list_categories'))

# === API Routes ===
def highlight_text(text, query):
    """Highlight search query matches in text with HTML spans."""
    if not query or not text:
        return text
    
    # Convert both text and query to lowercase for case-insensitive matching
    text_lower = text.lower()
    query_lower = query.lower()
    
    # If query not found in text, return original text
    if query_lower not in text_lower:
        return text
    
    result = []
    last_end = 0
    
    # Find all occurrences of query in text
    while True:
        start = text_lower.find(query_lower, last_end)
        if start == -1:
            break
            
        end = start + len(query)
        
        # Add text before match
        result.append(text[last_end:start])
        
        # Add highlighted match
        result.append(f'<span class="bg-yellow-200">{text[start:end]}</span>')
        
        last_end = end
    
    # Add remaining text
    result.append(text[last_end:])
    
    return ''.join(result)

@app.route('/api/search-suggestions')
def search_suggestions():
    """Get search suggestions for autocomplete."""
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    # Get matching blog titles
    blog_results = Blog.query.filter(
        Blog.title.ilike(f'%{query}%'),
        Blog.status == 'published',
        Blog.moderation_status != 'rejected'
    ).limit(5).all()
    
    for blog in blog_results:
        if blog.title.lower() not in [s['text'].lower() for s in suggestions]:
            suggestions.append({
                'text': blog.title,
                'type': 'blog',
                'url': url_for('view_blog', blog_id=blog.id)
            })
    
    # Get matching categories
    category_results = Category.query.filter(
        Category.name.ilike(f'%{query}%')
    ).limit(3).all()
    
    for category in category_results:
        suggestions.append({
            'text': category.name,
            'type': 'category',
            'url': url_for('category_view', category_id=category.id)
        })
    
    return jsonify(suggestions)

# === Application Setup ===
# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)