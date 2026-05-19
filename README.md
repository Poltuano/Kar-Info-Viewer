# Car Information Viewer

A professional desktop GUI application to view comprehensive car information and diagrams offline. Built with Python and PyQt5.

## ✨ Features

- 🚗 **Car Specifications Display** - View detailed specs including engine, transmission, dimensions, and more
- 📊 **Performance Metrics** - Horsepower, torque, acceleration, fuel efficiency, and top speed
- 🖼️ **Car Images & Diagrams** - Display car photos and component diagrams
- 🔍 **Advanced Search & Filter** - Find cars by make, model, or year
- 💾 **Database Integration** - Ready to integrate with your paid database source
- 📱 **Modern GUI** - Professional interface built with PyQt5
- ⚙️ **Maintenance Tracking** - View and track maintenance history
- 🔐 **Secure Configuration** - Environment-based configuration management
- 📝 **Comprehensive Logging** - Application logs for debugging

## 📋 Requirements

- Python 3.8 or higher
- PyQt5 5.15+
- Pillow (image handling)
- python-dotenv (configuration)
- requests (API calls)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Poltuano/Kar-Info-Viewer.git
cd Kar-Info-Viewer
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\\Scripts\\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DATABASE_HOST=your_database_server.com
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_NAME=your_database_name
API_ENDPOINT=https://your-api-endpoint.com/api
API_KEY=your_api_key_here
```

### 5. Integrate Your Database

Modify the following files with your database connection code:

- **`database/db_manager.py`** - Database connection and queries
- **`utils/data_fetcher.py`** - API/database data fetching

### 6. Run the Application

```bash
python main.py
```

## 📁 Project Structure

```
Kar-Info-Viewer/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore file
│
├── config/
│   ├── __init__.py
│   └── config.py                   # Configuration settings
│
├── database/
│   ├── __init__.py
│   ├── db_manager.py               # Database operations
│   └── models.py                   # Data models
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py              # Main window
├── gui/search_widget.py            # Search interface
│   └── car_detail_view.py          # Detail view with tabs
│
├── utils/
│   ├── __init__.py
│   ├── image_handler.py            # Image/diagram handling
│   ├── data_fetcher.py             # Database/API integration
│   └── validators.py               # Data validation
│
├── assets/
│   └── images/                     # Car diagrams and images
│
├── data/
│   └── sample_data.json            # Sample car data
│
README.md                           # This file
```

## 🔗 Database Integration

### Supported Database Types

- **PostgreSQL** - Default option
- **MySQL** - Fully supported
- **REST API** - For cloud-based databases

### Required Database Schema

Your database should include these tables:

**cars**
```sql
- id (PRIMARY KEY)
- make (VARCHAR)
- model (VARCHAR)
- year (INT)
- body_type (VARCHAR)
- color (VARCHAR)
- vin (VARCHAR)
- license_plate (VARCHAR)
- purchase_date (DATETIME)
- purchase_price (DECIMAL)
- current_mileage (INT)
- image_path (VARCHAR)
```

**car_specifications**
```sql
- id (PRIMARY KEY)
- car_id (FOREIGN KEY)
- engine_type (VARCHAR)
- horsepower (INT)
- torque (INT)
- transmission (VARCHAR)
- acceleration_0_100 (FLOAT)
- top_speed (INT)
- fuel_consumption_combined (FLOAT)
- fuel_type (VARCHAR)
- fuel_tank_capacity (FLOAT)
- cargo_capacity (INT)
- passenger_seats (INT)
- dimensions_length (FLOAT)
- dimensions_width (FLOAT)
- dimensions_height (FLOAT)
- weight (INT)
- wheelbase (FLOAT)
```

**maintenance_records**
```sql
- id (PRIMARY KEY)
- car_id (FOREIGN KEY)
- date (DATETIME)
- maintenance_type (VARCHAR)
- description (TEXT)
- cost (DECIMAL)
- mileage (INT)
- service_provider (VARCHAR)
- notes (TEXT)
```

## 🔧 Configuration

Edit `config/config.py` to customize:

- Database connection settings
- API endpoints and authentication
- Application logging level
- UI window dimensions
- Image handling settings
- Caching options

## 📸 Image Setup

1. Create `assets/images/` directory:
```bash
mkdir -p assets/images
```

2. Add your car images (JPG, PNG, GIF, BMP):
```
assets/images/
├── car1.jpg
├── car2.png
└── diagram.jpg
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Install requirements: `pip install -r requirements.txt`

### Issue: Database connection failed
**Solution:** 
- Check `.env` credentials
- Verify database server is running
- Ensure network connectivity
- Check firewall settings

### Issue: Images not displaying
**Solution:**
- Verify images exist in `assets/images/`
- Check supported format (JPG, PNG, GIF, BMP)
- Verify image paths in database

## 🚀 Performance Optimization

### For Large Datasets

1. **Enable Caching**:
   ```
   CACHE_ENABLED=true
   CACHE_DURATION=3600
   ```

2. **Database Optimization**:
   - Add indexes to frequently queried columns
   - Use pagination for large result sets
   - Implement query result limits

3. **UI Performance**:
   - Limit search results displayed
   - Load images asynchronously
   - Use lazy loading for maintenance records

## 🔐 Security Notes

- **Never commit `.env`** to version control
- **Use strong database passwords**
- **Keep API keys secure**
- **Validate all user input**
- **Use prepared statements** to prevent SQL injection
- **Implement proper error handling** without exposing sensitive data

## 📝 Logging

Application logs are saved to `car_viewer.log`. Check this file for debugging information and error messages.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues or questions:

1. Check the README guide
2. Review the code comments and TODO sections
3. Verify database connectivity
4. Check application logs in `car_viewer.log`

## 🎯 Roadmap

- [ ] Advanced filtering options
- [ ] Bulk import functionality
- [ ] Export car data to PDF/CSV
- [ ] Comparison tool for multiple cars
- [ ] Mobile companion app
- [ ] Dark mode theme
- [ ] Multi-language support

---

**Made with ❤️ for car enthusiasts and professionals**
