# Flask Blog Application

A modern blogging platform built with Flask, featuring user authentication, content moderation, and admin features.

## Features

- User authentication and authorization
- Blog post creation and management
- Category organization
- Content moderation system
- Admin dashboard with analytics
- Responsive design
- Search functionality
- Like and comment system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flask-blog.git
cd flask-blog
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
   - Copy `instance/config.example.py` to `instance/config.py`
   - Update the configuration values in `instance/config.py`

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the development server:
```bash
flask run
```

## Project Structure

```
/flask-blog
├── app.py                  # Application entry point
├── config.py              # Base configuration
├── requirements.txt       # Project dependencies
├── README.md
├── instance/             # Instance-specific config
│   ├── config.py        # Secret configuration
│   └── database/        # SQLite database
├── static/              # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Image assets
│   ├── uploads/        # User uploads
│   └── vendor/         # Third-party libraries
└── templates/          # Jinja2 templates
    ├── admin/         # Admin templates
    ├── auth/          # Authentication templates
    ├── blog/          # Blog-related templates
    └── category/      # Category templates
```

## Configuration

The application uses a multi-environment configuration system:

- `config.py`: Base configuration and environment-specific settings
- `instance/config.py`: Instance-specific secrets and keys (not version controlled)

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
python -m pytest
```

3. Check code style:
```bash
flake8
```

## Deployment

1. Set up production configuration:
   - Update `instance/config.py` with production settings
   - Set `FLASK_ENV=production`

2. Set up a production database:
   - Configure the database URI in `instance/config.py`
   - Run migrations: `flask db upgrade`

3. Set up a production server (e.g., Gunicorn):
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Aibin - Initial work and maintenance

## Acknowledgments

- Flask and its extensions
- Bootstrap for the UI framework
- All contributors and users of the application 