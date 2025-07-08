# ESG Reporting Web Application - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Emission Factors Management](#emission-factors-management)
4. [Measurements Data Entry](#measurements-data-entry)
5. [Supplier Management](#supplier-management)
6. [Reports and Analytics](#reports-and-analytics)
7. [Settings and Configuration](#settings-and-configuration)
8. [API Documentation](#api-documentation)
9. [Troubleshooting](#troubleshooting)

## Getting Started

Welcome to ESG Pro, your comprehensive platform for environmental, social, and governance reporting. This user guide will help you navigate through all the features and capabilities of the application.

### Accessing the Application

The ESG reporting application is accessible through your web browser at the provided URL. The application is designed to work on both desktop and mobile devices, providing a responsive experience across all platforms.

### User Interface Overview

The application features a clean, modern interface with a sidebar navigation menu that provides access to all major sections:

- **Dashboard**: Overview of your ESG metrics and key performance indicators
- **Emission Factors**: Manage emission factors for different activity categories
- **Measurements**: Enter and track actual consumption and activity data
- **Suppliers**: Manage supplier information and Scope 3 emissions data
- **Reports**: Generate comprehensive ESG reports and analytics
- **Settings**: Configure application preferences and integrations

## Dashboard Overview

The dashboard serves as your central hub for monitoring ESG performance. It provides real-time insights into your organization's environmental impact through interactive visualizations and key metrics.

### Key Metrics Display

The dashboard prominently displays four critical emission metrics:

- **Scope 1 Emissions**: Direct emissions from owned or controlled sources
- **Scope 2 Emissions**: Indirect emissions from purchased energy
- **Scope 3 Emissions**: All other indirect emissions in the value chain
- **Total Emissions**: Combined emissions across all scopes

Each metric is displayed with the current year's data and includes visual indicators to help you quickly assess performance.

### Emissions Visualizations

The dashboard includes several interactive charts:

**Emissions by Category**: A bar chart showing emissions breakdown by activity type (electricity, fuel, transportation, etc.). This helps identify the largest sources of emissions in your organization.

**Emissions by Scope**: A pie chart displaying the proportion of emissions from each scope. This visualization helps understand the distribution of direct versus indirect emissions.

**Monthly Emissions Trend**: A line chart showing emissions patterns over time. This trend analysis helps identify seasonal patterns and track progress toward reduction goals.

### Recent Measurements

The dashboard displays the most recently entered measurement data, providing visibility into current data collection activities and ensuring data freshness.

## Emission Factors Management

Emission factors are the foundation of accurate emissions calculations. This section allows you to manage the conversion factors used to calculate emissions from activity data.

### Understanding Emission Factors

Emission factors represent the amount of greenhouse gas emissions produced per unit of activity. For example, an electricity emission factor might be expressed as kilograms of CO2 equivalent per kilowatt-hour (kg CO2e/kWh).

### Adding New Emission Factors

To add a new emission factor:

1. Navigate to the Emission Factors page
2. Click the "Add Emission Factor" button
3. Fill in the required information:
   - **Name**: Descriptive name for the emission factor
   - **Category**: Activity category (electricity, fuel, transportation, etc.)
   - **Scope**: Relevant GHG Protocol scope (1, 2, or 3)
   - **Factor Value**: Numerical emission factor value
   - **Unit**: Unit of measurement (kg CO2e/kWh, kg CO2e/liter, etc.)
   - **Source**: Reference source for the emission factor
   - **Valid From/To**: Date range for factor validity

### Managing Existing Factors

The emission factors table displays all configured factors with options to:

- **Edit**: Modify existing emission factor details
- **Delete**: Remove outdated or incorrect factors
- **Filter**: Search and filter factors by category, scope, or other criteria
- **Sort**: Organize factors by different attributes

### Best Practices for Emission Factors

- Use the most recent and geographically appropriate emission factors
- Document the source and methodology for each factor
- Regularly review and update factors to maintain accuracy
- Consider using location-based factors for Scope 2 emissions where available

## Measurements Data Entry

The measurements section is where you input actual activity data that will be converted to emissions using your configured emission factors.

### Data Entry Process

1. **Select Category**: Choose the appropriate emission category for your data
2. **Enter Activity Data**: Input the quantity of activity (energy consumed, fuel used, distance traveled, etc.)
3. **Specify Date Range**: Define the period covered by the measurement
4. **Add Context**: Include relevant notes or additional information
5. **Save**: Submit the data for processing

### Supported Measurement Categories

The application supports various measurement categories:

**Energy Consumption**:
- Electricity usage (kWh)
- Natural gas consumption (cubic meters or therms)
- Heating oil usage (liters or gallons)
- Steam consumption (pounds or kilograms)

**Transportation**:
- Vehicle fuel consumption (liters or gallons)
- Distance traveled by mode (kilometers or miles)
- Public transportation usage
- Air travel (passenger-kilometers)

**Waste and Water**:
- Waste generation by type (kilograms or tons)
- Water consumption (cubic meters or gallons)
- Wastewater treatment (cubic meters)

**Refrigerants and Other**:
- Refrigerant leakage (kilograms)
- Process emissions (various units)
- Fugitive emissions

### Data Validation and Quality

The application includes built-in validation to ensure data quality:

- **Range Checks**: Alerts for values outside expected ranges
- **Consistency Checks**: Validation against historical data patterns
- **Completeness Monitoring**: Tracking of missing data points
- **Unit Validation**: Verification of measurement units

## Supplier Management

Scope 3 emissions often represent the largest portion of an organization's carbon footprint. The supplier management section helps you collect and manage emissions data from your supply chain.

### Supplier Onboarding

To add a new supplier:

1. Navigate to the Suppliers page
2. Click "Add Supplier"
3. Enter supplier information:
   - Company name and contact details
   - Industry sector and business description
   - Spend category and procurement volume
   - ESG contact person information

### Data Collection Workflows

The application supports various approaches to supplier data collection:

**Direct Data Collection**: Suppliers can be invited to enter their emissions data directly through the platform.

**Survey Distribution**: Standardized questionnaires can be sent to suppliers to collect emissions and sustainability information.

**Spend-Based Calculations**: For suppliers without specific emissions data, spend-based emission factors can be applied to procurement amounts.

**Hybrid Approaches**: Combination of direct data and estimation methods based on data availability and supplier engagement levels.

### Supplier Engagement Tracking

Monitor supplier participation and data quality through:

- **Response Rates**: Track which suppliers have provided data
- **Data Completeness**: Monitor the quality and completeness of supplier submissions
- **Engagement Timeline**: Track communication and follow-up activities
- **Performance Metrics**: Assess supplier ESG performance over time

## Reports and Analytics

The reports section provides comprehensive analytics and reporting capabilities to support both internal decision-making and external reporting requirements.

### Executive Summary Reports

Generate high-level summaries suitable for executive audiences:

- **Total Emissions Overview**: Summary of emissions across all scopes
- **Key Performance Indicators**: Critical metrics and trends
- **Target Progress**: Status of emissions reduction goals
- **Year-over-Year Comparisons**: Performance trends and changes

### Detailed Analytics

Access in-depth analysis through multiple report tabs:

**Emissions Analysis**:
- Detailed breakdown by scope and category
- Trend analysis and pattern identification
- Comparative analysis across time periods
- Hotspot identification for reduction opportunities

**Target Progress**:
- Science-based target tracking
- Progress visualization and forecasting
- Gap analysis and action planning
- Milestone achievement monitoring

**Trends and Forecasts**:
- Historical trend analysis
- Predictive modeling and forecasting
- Scenario analysis for different reduction strategies
- Seasonal pattern identification

**Compliance Monitoring**:
- Regulatory requirement tracking
- Reporting standard compliance (GRI, SASB, TCFD)
- Data quality assessment
- Verification status monitoring

### Export and Sharing

Reports can be exported in multiple formats:

- **PDF Reports**: Professional formatted reports for external sharing
- **Excel Spreadsheets**: Detailed data for further analysis
- **CSV Data**: Raw data for integration with other systems
- **Interactive Dashboards**: Shareable online visualizations

## Settings and Configuration

The settings section allows you to customize the application to meet your organization's specific needs and preferences.

### Company Information

Configure your organization's basic information:

- Company name and industry sector
- Reporting year and fiscal calendar
- Currency and measurement units
- Geographic location and time zone

### User Management

Manage user access and permissions:

- **User Roles**: Administrator, Manager, Analyst, Viewer
- **Access Controls**: Feature-specific permissions
- **Authentication**: Password policies and security settings
- **Activity Monitoring**: User action logging and audit trails

### Notification Preferences

Configure how and when you receive updates:

- **Email Notifications**: General system notifications
- **Report Reminders**: Deadline and milestone alerts
- **Data Quality Alerts**: Warnings about data issues
- **Weekly Digests**: Summary reports and updates

### Data Management

Control how your data is handled:

- **Auto-calculation**: Automatic emissions calculations
- **Data Retention**: How long data is stored
- **Backup Frequency**: Automated backup schedules
- **Export Options**: Data portability settings

### API and Integrations

Configure connections with external systems:

- **API Keys**: Authentication for external access
- **Webhook URLs**: Real-time notification endpoints
- **Third-party Integrations**: Connections with other platforms
- **Data Synchronization**: Automated data exchange settings

## API Documentation

The ESG reporting platform provides a comprehensive REST API for integration with external systems and automated data exchange.

### Authentication

API access requires authentication using API keys:

```
Authorization: Bearer YOUR_API_KEY
```

API keys can be generated and managed through the Settings section of the application.

### Core Endpoints

**Emission Factors**:
- `GET /api/emission-factors` - Retrieve all emission factors
- `POST /api/emission-factors` - Create new emission factor
- `PUT /api/emission-factors/{id}` - Update existing factor
- `DELETE /api/emission-factors/{id}` - Remove emission factor

**Measurements**:
- `GET /api/measurements` - Retrieve measurement data
- `POST /api/measurements` - Submit new measurements
- `PUT /api/measurements/{id}` - Update measurement data
- `DELETE /api/measurements/{id}` - Remove measurements

**Suppliers**:
- `GET /api/suppliers` - List all suppliers
- `POST /api/suppliers` - Add new supplier
- `PUT /api/suppliers/{id}` - Update supplier information
- `DELETE /api/suppliers/{id}` - Remove supplier

**Dashboard Data**:
- `GET /api/dashboard/overview` - Get dashboard summary
- `GET /api/dashboard/emissions-by-scope` - Scope breakdown
- `GET /api/dashboard/emissions-by-category` - Category analysis
- `GET /api/dashboard/monthly-trend` - Time series data

### Data Formats

All API endpoints use JSON format for data exchange. Example request:

```json
{
  "name": "Electricity Grid Factor",
  "category": "electricity",
  "scope": 2,
  "factor_value": 0.45,
  "unit": "kg CO2e/kWh",
  "source": "National Grid",
  "valid_from": "2024-01-01",
  "valid_to": "2024-12-31"
}
```

### Error Handling

The API returns standard HTTP status codes and detailed error messages:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Troubleshooting

### Common Issues and Solutions

**Data Not Displaying**:
- Check internet connection and refresh the page
- Verify that data has been entered for the selected time period
- Ensure emission factors are configured for the relevant categories

**Calculation Errors**:
- Verify that emission factors are correctly configured
- Check that measurement units match emission factor units
- Review data entry for accuracy and completeness

**Performance Issues**:
- Clear browser cache and cookies
- Try accessing the application from a different browser
- Contact support if issues persist

**Access Problems**:
- Verify your user credentials and permissions
- Check that your account has not been suspended
- Contact your system administrator for access issues

### Getting Support

For technical support or questions about using the ESG reporting platform:

- **Documentation**: Refer to this user guide and online help resources
- **Email Support**: Contact the support team for technical assistance
- **Training Resources**: Access video tutorials and training materials
- **Community Forum**: Connect with other users and share best practices

### Data Backup and Recovery

The application automatically backs up your data according to the configured schedule. In case of data loss:

1. Contact support immediately
2. Provide details about when the data was last seen
3. Avoid entering duplicate data until recovery is complete
4. Follow support team instructions for data restoration

This comprehensive user guide provides the foundation for effectively using the ESG reporting web application. Regular updates and additional resources will be provided as the platform evolves and new features are added.

