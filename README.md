# Tracking Number Generator API

A production-ready REST API built with Django REST Framework that generates unique tracking numbers for parcels. The API is designed for high concurrency, horizontal scalability, and includes comprehensive logging, monitoring, and testing.

## 🚀 Features

- **Unique Tracking Number Generation**: Generates tracking numbers matching regex `^[A-Z0-9]{1,16}$`
- **High Concurrency Support**: Thread-safe and designed for concurrent execution
- **Comprehensive Validation**: Strong input validation for all parameters
- **Monitoring & Logging**: Structured logging with correlation IDs and metrics collection
- **Production Ready**: Includes error handling, health checks, and deployment configuration
- **Fully Tested**: Comprehensive unit tests with mocking

## 📋 API Specification

### Endpoint
\`\`\`
GET /next-tracking-number
\`\`\`

### Required Query Parameters
- `origin_country_id`: ISO 3166-1 alpha-2 format (e.g., "MY")
- `destination_country_id`: ISO 3166-1 alpha-2 format (e.g., "ID")
- `weight`: Float in kg, up to 3 decimal places (e.g., "1.234")
- `created_at`: RFC 3339 timestamp format (e.g., "2018-11-20T19:29:32+08:00")
- `customer_id`: UUID (e.g., "de619854-b59b-425e-9db4-943979e1bd49")
- `customer_name`: String (e.g., "RedBox Logistics")
- `customer_slug`: Kebab-case string (e.g., "redbox-logistics")

### Response Format
\`\`\`json
{
  "tracking_number": "MYID123456789",
  "created_at": "2025-06-30T13:45:00+08:00",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "request_metadata": {
    "origin_country": "MY",
    "destination_country": "ID",
    "weight_kg": "1.234",
    "customer_slug": "redbox-logistics"
  }
}
\`\`\`

## 🛠️ Tech Stack

- **Framework**: Django 5.0.1 + Django REST Framework 3.14.0
- **Database**: PostgreSQL (production) / SQLite (development)
- **Deployment**: Docker, Gunicorn, WhiteNoise
- **Monitoring**: Structured logging, metrics collection
- **Testing**: Django Test Framework with comprehensive coverage

## 🏗️ Project Structure

\`\`\`
tracking_api/
├── tracking_api/          # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── tracking/             # Main application
│   ├── models.py         # Database models
│   ├── serializers.py    # Request/response serializers
│   ├── services.py       # Business logic
│   ├── views.py          # API endpoints
│   ├── exceptions.py     # Custom exceptions
│   ├── middleware.py     # Request logging middleware
│   └── tests/           # Comprehensive test suite
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Local development setup
└── README.md           # This file
\`\`\`

## 🚀 Quick Start

### Local Development

1. **Clone and setup**:
\`\`\`bash
git clone <repository-url>
cd tracking-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

2. **Environment setup**:
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

3. **Database setup**:
\`\`\`bash
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
\`\`\`

4. **Run the server**:
\`\`\`bash
python manage.py runserver
\`\`\`

The API will be available at `http://localhost:8000`

### Using Docker

1. **Build and run**:
\`\`\`bash
docker-compose up --build
\`\`\`

2. **Run migrations**:
\`\`\`bash
docker-compose exec web python manage.py migrate
\`\`\`

## 📝 API Usage Examples

### Generate Tracking Number
\`\`\`bash
curl -X GET "http://localhost:8000/next-tracking-number" \
  -G \
  -d "origin_country_id=MY" \
  -d "destination_country_id=ID" \
  -d "weight=1.234" \
  -d "created_at=2018-11-20T19:29:32+08:00" \
  -d "customer_id=de619854-b59b-425e-9db4-943979e1bd49" \
  -d "customer_name=RedBox Logistics" \
  -d "customer_slug=redbox-logistics"
\`\`\`

### Health Check
\`\`\`bash
curl -X GET "http://localhost:8000/health"
\`\`\`

### Metrics
\`\`\`bash
curl -X GET "http://localhost:8000/metrics"
\`\`\`

## 🧪 Testing

### Run All Tests
\`\`\`bash
python manage.py test
\`\`\`

### Run Specific Test Module
\`\`\`bash
python manage.py test tracking.tests.test_services
python manage.py test tracking.tests.test_views
python manage.py test tracking.tests.test_serializers
\`\`\`

### Run Tests with Coverage
\`\`\`bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML coverage report
\`\`\`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required in production |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1,0.0.0.0` |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | Empty (allows all in debug) |

### Database Configuration

**SQLite (Development)**:
\`\`\`
DATABASE_URL=sqlite:///db.sqlite3
\`\`\`

**PostgreSQL (Production)**:
\`\`\`
DATABASE_URL=postgresql://user:password@host:port/database
\`\`\`

## 📊 Monitoring & Logging

### Structured Logging
The API includes comprehensive structured logging with:
- Correlation IDs for request tracking
- Performance metrics
- Error tracking
- Request/response logging

### Metrics Collection
- API call counts
- Response times
- Success/failure rates
- Tracking number generation statistics

### Health Checks
- `/health` - Basic health check
- `/metrics` - Performance metrics
- Admin interface at `/admin/`

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI and login**:
\`\`\`bash
heroku login
\`\`\`

2. **Create Heroku app**:
\`\`\`bash
heroku create your-tracking-api
\`\`\`

3. **Set environment variables**:
\`\`\`bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-tracking-api.herokuapp.com
\`\`\`

4. **Add PostgreSQL addon**:
\`\`\`bash
heroku addons:create heroku-postgresql:mini
\`\`\`

5. **Deploy**:
\`\`\`bash
git push heroku main
\`\`\`

### AWS/GCP Deployment

The application includes Docker configuration for easy deployment to any cloud provider:

1. **Build Docker image**:
\`\`\`bash
docker build -t tracking-api .
\`\`\`

2. **Push to container registry**:
\`\`\`bash
# For AWS ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin account.dkr.ecr.region.amazonaws.com
docker tag tracking-api:latest account.dkr.ecr.region.amazonaws.com/tracking-api:latest
docker push account.dkr.ecr.region.amazonaws.com/tracking-api:latest
\`\`\`

## 🔒 Security Considerations

- **Input Validation**: Comprehensive validation for all input parameters
- **SQL Injection Protection**: Using Django ORM prevents SQL injection
- **CORS Configuration**: Configurable CORS settings for production
- **Secret Management**: Environment-based secret management
- **Rate Limiting**: Can be added using django-ratelimit if needed

## 🎯 Algorithm Details

### Tracking Number Generation

The tracking number generation algorithm ensures uniqueness through:

1. **Deterministic Hash**: Creates a hash from input parameters
2. **Timestamp Component**: Adds microsecond timestamp for temporal uniqueness
3. **Correlation ID**: Includes request correlation ID for additional entropy
4. **Base36 Encoding**: Converts to alphanumeric format (0-9, A-Z)
5. **Country Code Prefix**: Adds origin/destination country codes for context

This approach ensures:
- **Uniqueness**: Even under high concurrency
- **Deterministic**: Same inputs produce same output (useful for idempotency)
- **Scalable**: No database lookups required for generation
- **Format Compliance**: Matches required regex `^[A-Z0-9]{1,16}$`

## 🐛 Error Handling

The API provides comprehensive error handling with:

- **Validation Errors**: 400 Bad Request with detailed field errors
- **Server Errors**: 500 Internal Server Error with correlation IDs
- **Custom Exceptions**: Structured error responses
- **Logging**: All errors logged with context

### Example Error Response
\`\`\`json
{
  "error": "Invalid request parameters",
  "details": {
    "origin_country_id": ["Origin country ID must be ISO 3166-1 alpha-2 format (e.g., 'MY')"]
  },
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
\`\`\`

## 📈 Performance

- **Low Latency**: Optimized for sub-100ms response times
- **High Concurrency**: Thread-safe implementation
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Optimization**: Indexed fields for fast queries
- **Caching**: Response caching can be added if needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the logs for correlation IDs when reporting errors
- Include request parameters (without sensitive data) when reporting issues

---

**Built with ❤️ using Django REST Framework**
