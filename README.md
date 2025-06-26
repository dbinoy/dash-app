# User Login Telemetry Dash App

This project is a Dash application designed to visualize user login telemetry data. It provides various charts and metrics to help analyze user engagement and application usage across different offices.

## Project Structure

```
user-login-telemetry-dash-app
├── src
│   ├── app.py                     # Main entry point of the Dash application
│   ├── components                 # Contains reusable components for the dashboard
│   │   ├── filters.py             # Filter components for data visualization
│   │   ├── summary_cards.py       # Summary cards displaying key metrics
│   │   ├── weekly_login_trends.py # Chart for weekly login trends
│   │   ├── app_usage_by_office.py# Chart for application usage by office
│   │   ├── user_activity_distribution.py # Chart for user activity distribution
│   │   ├── weekly_app_popularity.py # Chart for weekly app popularity
│   │   └── data_table_view.py     # Data table view for detailed information
│   └── assets
│       └── styles.css             # Custom styles for the application
├── requirements.txt                # Lists dependencies for the application
└── README.md                       # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd user-login-telemetry-dash-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

4. Open your web browser and navigate to `http://127.0.0.1:8050` to view the dashboard.

## Features

- **User Filters**: Interactive filters to customize the data displayed on the dashboard.
- **Summary Cards**: Quick insights into key metrics related to user logins and application usage.
- **Charts**: Various visualizations including weekly login trends, application usage by office, user engagement heatmaps, and more.
- **Data Table**: A detailed view of user activity and application usage statistics.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.