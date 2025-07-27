# GenXData Unified Generators Documentation

## Overview

GenXData provides **175 pre-configured generators** across **9 specialized collections** to simplify data generation for various domains. These generators eliminate the need to manually configure strategy parameters, allowing you to reference them by name in your data generation configurations.

## Generator Collections Summary

| Collection | Generators | Focus Area |
|-----------|------------|------------|
| **Generic** | 32 | Universal data types (names, dates, numbers, patterns) |
| **Business** | 10 | Corporate data (companies, jobs, budgets, projects) |
| **E-commerce** | 16 | Online retail (products, orders, payments, transactions) |
| **Education** | 19 | Academic data (students, grades, courses, schools) |
| **Geographic** | 16 | Location data (addresses, coordinates, regions) |
| **Healthcare** | 14 | Medical data (patients, conditions, vital signs) |
| **IoT Sensors** | 20 | Environmental and sensor data |
| **Technology** | 24 | IT systems (devices, software, APIs, performance) |
| **Transportation** | 24 | Vehicle and logistics data |
| **TOTAL** | **175** | Comprehensive data generation coverage |

## How to Use Generators

### Basic Usage
```yaml
columns:
  name:
    generator: "FULL_NAME"  # Reference by name
  age:
    generator: "PERSON_AGE"
  salary:
    generator: "SALARY"
```

### Advanced Configuration
```yaml
columns:
  employee_id:
    generator: "EMPLOYEE_ID"
  department:
    generator: "DEPARTMENT"
  hire_date:
    generator: "RECENT_DATE"
  email:
    generator: "EMAIL_PATTERN"
```

## Complete Generator Reference

### 1. Generic Generators (32 total)

#### Name Generators
- **PERSON_NAME**: Random first names (any gender, title case)
- **FULL_NAME**: Complete names with first and last
- **LAST_NAME**: Surnames in uppercase
- **FIRST_NAME_MALE**: Male first names
- **FIRST_NAME_FEMALE**: Female first names

#### Date & Time Generators
- **BIRTH_DATE**: Birth dates (1950-2005)
- **RECENT_DATE**: Recent dates (2020-2024)
- **WEEKEND_DATES**: Distributed weekend dates
- **HISTORICAL_DATES**: Dates with historical distribution
- **WORKING_HOURS**: Business hours (09:00-17:00)
- **EVENING_HOURS**: Evening times (18:00-23:59)
- **MORNING_HOURS**: Morning times (06:00-11:59)
- **BUSINESS_HOURS**: Distributed business hours

#### Number Generators
- **PERSON_AGE**: Ages between 18-100
- **SALARY**: Salary range (30,000-150,000)
- **PERCENTAGE**: Percentages (0-100)
- **WEIGHT_KG**: Realistic weight distribution
- **HEIGHT_CM**: Realistic height distribution
- **INCOME_BRACKETS**: Income with realistic distribution

#### Sequential Generators
- **EMPLOYEE_ID**: Sequential employee IDs starting from 1001
- **BATCH_NUMBER**: Sequential batch numbers with decimal steps

#### Pattern Generators
- **PHONE_NUMBER**: US phone format (XXX-XXX-XXXX)
- **EMAIL_PATTERN**: Email addresses with realistic patterns
- **SSN**: Social Security Numbers (XXX-XX-XXXX)
- **PRODUCT_SKU**: Product codes (ABC-1234-XY)
- **LICENSE_PLATE**: License plates (ABC1234)

#### Choice Generators
- **DEPARTMENT**: Company departments with distribution
- **PRIORITY_LEVEL**: Priority levels (Low, Medium, High, Critical)
- **EDUCATION_LEVEL**: Education levels with realistic distribution

#### Data Manipulation
- **NULL_VALUES**: Delete strategy for conditional nulls
- **REPLACE_PLACEHOLDER**: Replace "TBD" with "Not Available"
- **GENDER_MAPPING**: Map "M" to "Male"

### 2. Business Generators (10 total)

#### Company Data
- **COMPANY_NAME**: Technology company names
- **INDUSTRY**: Industry categories with realistic distribution
- **COMPANY_SIZE**: Company size categories (Startup to Enterprise)

#### Employee Data
- **JOB_TITLE**: Job positions with distribution
- **EXPERIENCE_LEVEL**: Career levels (Entry to Executive)

#### Financial Data
- **BUDGET_RANGE**: Project budgets with realistic ranges
- **QUARTERLY_REVENUE**: Revenue with business distribution

#### Project Management
- **PROJECT_STATUS**: Project statuses (Planning, In Progress, etc.)
- **MEETING_TIMES**: Business meeting times
- **FISCAL_YEAR_DATES**: Fiscal year quarters

### 3. E-commerce Generators (16 total)

#### Product Data
- **PRODUCT_CATEGORY**: Product categories with market distribution
- **PRODUCT_PRICE**: Product prices with realistic ranges
- **CUSTOMER_RATING**: Star ratings (1-5 stars)

#### Order Management
- **ORDER_STATUS**: Order statuses (Pending to Delivered)
- **ORDER_ID**: Order IDs (ORD-12345678-ABC)
- **SHIPPING_METHOD**: Shipping options with preferences

#### Payment Systems
- **PAYMENT_METHOD**: Payment methods with usage distribution
- **TRANSACTION_AMOUNT**: Transaction amounts
- **TRANSACTION_ID**: Transaction IDs (TXN123456789ABC)
- **CREDIT_CARD_NUMBER**: Credit card numbers (4XXX-XXXX-XXXX-XXXX)
- **CREDIT_SCORE**: Credit scores with realistic distribution

#### Financial Products
- **ACCOUNT_TYPE**: Bank account types
- **CURRENCY**: Currency codes with usage distribution
- **DISCOUNT_PERCENTAGE**: Discount percentages
- **INVOICE_NUMBER**: Invoice numbers
- **SUBSCRIPTION_TYPE**: Subscription tiers

### 4. Education Generators (19 total)

#### Student Performance
- **STUDENT_GRADE**: Letter grades (A+ to F) with realistic distribution
- **GPA**: Grade Point Averages with academic distribution
- **ATTENDANCE_RATE**: Attendance percentages

#### Academic Structure
- **ACADEMIC_YEAR**: Academic years (2020-2025)
- **SEMESTER**: Semesters (Fall, Spring, Summer)
- **SCHOOL_LEVEL**: Education levels (Elementary to Graduate)
- **CLASS_YEAR**: Student years (Freshman to Senior)

#### Subjects & Activities
- **MAJOR**: Academic majors with popularity distribution
- **EXTRACURRICULAR_ACTIVITY**: Student activities
- **COURSE_CODE**: Course codes (ABC123, MATH101)
- **CLASSROOM_NUMBER**: Room numbers (A101, B205A)

#### Education System
- **TEACHER_EXPERIENCE**: Years of teaching experience
- **SCHOOL_TYPE**: School types (Public, Private, Charter)
- **ENROLLMENT_STATUS**: Student enrollment status
- **TUITION_FEES**: Tuition amounts with realistic ranges

#### Identifiers
- **STUDENT_ID**: Student IDs (STU1234567)

### 5. Geographic Generators (16 total)

#### US Location Data
- **US_STATE**: US states with population-based distribution
- **MAJOR_CITY**: Major US cities with population weights
- **ZIP_CODE**: 5-digit ZIP codes
- **ZIP_CODE_PLUS_FOUR**: Extended ZIP codes (12345-6789)

#### International Data
- **COUNTRY**: Countries with realistic distribution
- **TIMEZONE**: Time zones with usage distribution

#### Coordinates
- **LATITUDE**: Global latitude coordinates (-90 to 90)
- **LONGITUDE**: Global longitude coordinates (-180 to 180)
- **US_LATITUDE**: US-specific latitude range
- **US_LONGITUDE**: US-specific longitude range

#### Address Components
- **STREET_ADDRESS**: Street addresses with realistic patterns
- **APARTMENT_NUMBER**: Apartment/unit numbers
- **BUILDING_NUMBER**: Building numbers
- **POSTAL_CODE**: International postal codes
- **REGION**: Geographic regions
- **CITY_POPULATION**: City population ranges

### 6. Healthcare Generators (14 total)

#### Patient Demographics
- **PATIENT_AGE**: Patient ages with healthcare distribution
- **BLOOD_TYPE**: Blood types with realistic prevalence
- **PATIENT_ID**: Patient IDs (PT123456AB)
- **MEDICAL_RECORD_NUMBER**: Medical record numbers

#### Medical Conditions
- **MEDICAL_CONDITION**: Common medical conditions
- **PRESCRIPTION_MEDICATION**: Common medications
- **HOSPITAL_DEPARTMENT**: Hospital departments

#### Vital Signs
- **VITAL_SIGNS_BP_SYSTOLIC**: Blood pressure (systolic)
- **VITAL_SIGNS_HEART_RATE**: Heart rate ranges
- **BODY_TEMPERATURE**: Body temperature with fever distribution

#### Healthcare System
- **INSURANCE_TYPE**: Insurance types with distribution
- **APPOINTMENT_TIMES**: Medical appointment times
- **VISIT_REASON**: Reasons for medical visits
- **LAB_TEST_TYPE**: Laboratory test types

### 7. IoT Sensors Generators (20 total)

#### Environmental Sensors
- **TEMPERATURE_CELSIUS**: Temperature readings with seasonal distribution
- **HUMIDITY_PERCENT**: Humidity levels with comfort ranges
- **PRESSURE_HPA**: Atmospheric pressure readings
- **LIGHT_LUX**: Light intensity measurements
- **SOUND_DB**: Sound level measurements
- **WIND_SPEED_KMH**: Wind speed readings

#### Device Status
- **BATTERY_LEVEL_PERCENT**: Battery levels with usage patterns
- **SIGNAL_STRENGTH_DBM**: Signal strength measurements
- **DEVICE_STATUS**: Device operational status
- **CONNECTIVITY_TYPE**: Connection types (WiFi, Cellular, etc.)

#### Air Quality
- **AIR_QUALITY_INDEX**: AQI measurements
- **CO2_PPM**: Carbon dioxide levels
- **PARTICULATE_MATTER**: PM2.5 measurements

#### Sensor Identification
- **SENSOR_ID**: Sensor identifiers (SENS-123456)
- **DEVICE_MAC_ADDRESS**: MAC addresses for IoT devices

#### Time-based Data
- **READING_TIMESTAMP**: Sensor reading timestamps
- **UPTIME_HOURS**: Device uptime measurements
- **DATA_TRANSMISSION_RATE**: Data transmission rates
- **MAINTENANCE_SCHEDULE**: Maintenance intervals
- **CALIBRATION_DATE**: Sensor calibration dates

### 8. Technology Generators (24 total)

#### Device & System Data
- **DEVICE_TYPE**: Device types with market distribution
- **OPERATING_SYSTEM**: OS with market share distribution
- **BROWSER**: Web browsers with usage statistics
- **SCREEN_RESOLUTION**: Screen resolutions with popularity

#### Development & Programming
- **PROGRAMMING_LANGUAGE**: Languages with popularity distribution
- **DATABASE_TYPE**: Database systems with usage patterns
- **CLOUD_PROVIDER**: Cloud providers with market share
- **GITHUB_USERNAME**: GitHub usernames
- **COMMIT_HASH**: Git commit hashes
- **DOCKER_IMAGE_TAG**: Docker image tags

#### Social Media & Web
- **SOCIAL_MEDIA_PLATFORM**: Platforms with user distribution
- **USER_AGENT**: Browser user agents
- **SESSION_DURATION_MINUTES**: User session lengths

#### Performance & Monitoring
- **API_RESPONSE_TIME_MS**: API response times
- **HTTP_STATUS_CODE**: HTTP status codes with occurrence rates
- **LOG_LEVEL**: Logging levels
- **CPU_USAGE_PERCENT**: CPU utilization
- **MEMORY_USAGE_GB**: Memory usage patterns
- **BANDWIDTH_MBPS**: Network bandwidth

#### Security & Identification
- **IP_ADDRESS**: IP addresses
- **MAC_ADDRESS**: MAC addresses
- **UUID**: Universally unique identifiers
- **API_KEY**: API keys
- **JWT_TOKEN**: JWT tokens

### 9. Transportation Generators (24 total)

#### Vehicle Data
- **VEHICLE_TYPE**: Vehicle types with market distribution
- **VEHICLE_MANUFACTURER**: Car manufacturers with market share
- **VEHICLE_COLOR**: Vehicle colors with popularity
- **FUEL_TYPE**: Fuel types with realistic distribution
- **VEHICLE_YEAR**: Vehicle years with age distribution

#### Vehicle Performance
- **MILEAGE**: Vehicle mileage with realistic ranges
- **SPEED_KMH**: Vehicle speeds with traffic patterns
- **FUEL_EFFICIENCY**: Miles per gallon ratings
- **ENGINE_SIZE**: Engine sizes with distribution

#### Logistics & Shipping
- **SHIPPING_STATUS**: Package delivery statuses
- **TRANSPORTATION_MODE**: Transport methods
- **DISTANCE_KM**: Travel distances
- **DELIVERY_TIME_HOURS**: Delivery timeframes
- **CARGO_TYPE**: Cargo categories
- **CARGO_WEIGHT_KG**: Cargo weights

#### Aviation
- **FLIGHT_STATUS**: Flight statuses (On Time, Delayed, etc.)
- **AIRCRAFT_TYPE**: Aircraft models
- **FLIGHT_DURATION_HOURS**: Flight durations
- **ALTITUDE_FEET**: Flight altitudes

#### Identifiers & Tracking
- **VEHICLE_VIN**: Vehicle identification numbers
- **TRACKING_NUMBER**: Package tracking numbers
- **ROUTE_ID**: Route identifiers
- **DRIVER_LICENSE**: Driver's license numbers

## Strategy Implementation Mapping

### Strategy Types Used
- **Random Name Strategy**: Name generation with gender/case options
- **Date Generator Strategy**: Date ranges with format control
- **Time Range Strategy**: Time periods with format options
- **Number Range Strategy**: Numeric ranges with bounds
- **Series Strategy**: Sequential numbering with steps
- **Pattern Strategy**: Regex-based pattern generation
- **Distributed Choice Strategy**: Weighted choice selection
- **Distributed Number Range Strategy**: Multi-range numeric distribution
- **Distributed Date Range Strategy**: Multi-period date distribution
- **Distributed Time Range Strategy**: Multi-period time distribution
- **Replacement Strategy**: Value replacement operations
- **Delete Strategy**: Conditional data deletion
- **Concat Strategy**: String concatenation operations

### Implementation Statistics
- **Total Generators**: 175
- **Strategy Types Used**: 12 out of 13 available
- **Domain Coverage**: 9 specialized areas
- **Pattern Generators**: 15 (IDs, codes, formats)
- **Distributed Generators**: 89 (realistic distributions)
- **Time/Date Generators**: 23 (various time formats)
- **Choice Generators**: 31 (categorical data)
- **Numeric Generators**: 41 (ranges and distributions)

## Best Practices

### 1. Choosing the Right Generator
- Use domain-specific generators for specialized data
- Generic generators work well for universal data types
- Consider distribution patterns for realistic data

### 2. Combining Generators
```yaml
columns:
  patient_id:
    generator: "PATIENT_ID"
  age:
    generator: "PATIENT_AGE"  # Healthcare-specific age distribution
  blood_type:
    generator: "BLOOD_TYPE"
  condition:
    generator: "MEDICAL_CONDITION"
```

### 3. Performance Considerations
- Pattern generators may be slower for large datasets
- Distributed generators provide more realistic data
- Simple range generators are fastest for basic needs

### 4. Data Consistency
- Use related generators from the same domain
- Consider sequential generators for IDs and references
- Maintain logical relationships between fields

## Extended Usage Examples

### Complete E-commerce Dataset
```yaml
columns:
  order_id:
    generator: "ORDER_ID"
  customer_name:
    generator: "FULL_NAME"
  product_category:
    generator: "PRODUCT_CATEGORY"
  price:
    generator: "PRODUCT_PRICE"
  payment_method:
    generator: "PAYMENT_METHOD"
  order_status:
    generator: "ORDER_STATUS"
  shipping_method:
    generator: "SHIPPING_METHOD"
  rating:
    generator: "CUSTOMER_RATING"
```

### Healthcare Patient Records
```yaml
columns:
  patient_id:
    generator: "PATIENT_ID"
  patient_name:
    generator: "FULL_NAME"
  age:
    generator: "PATIENT_AGE"
  blood_type:
    generator: "BLOOD_TYPE"
  condition:
    generator: "MEDICAL_CONDITION"
  department:
    generator: "HOSPITAL_DEPARTMENT"
  heart_rate:
    generator: "VITAL_SIGNS_HEART_RATE"
  temperature:
    generator: "BODY_TEMPERATURE"
  insurance:
    generator: "INSURANCE_TYPE"
```

### IoT Sensor Network
```yaml
columns:
  sensor_id:
    generator: "SENSOR_ID"
  temperature:
    generator: "TEMPERATURE_CELSIUS"
  humidity:
    generator: "HUMIDITY_PERCENT"
  pressure:
    generator: "PRESSURE_HPA"
  light_level:
    generator: "LIGHT_LUX"
  sound_level:
    generator: "SOUND_DB"
  battery_level:
    generator: "BATTERY_LEVEL_PERCENT"
  device_status:
    generator: "DEVICE_STATUS"
```

## Conclusion

With 175 pre-configured generators across 9 specialized domains, GenXData provides comprehensive coverage for most data generation needs. These generators eliminate configuration complexity while providing realistic, distributed data that closely matches real-world patterns.

The generators are designed to work seamlessly together, allowing you to create complex, multi-domain datasets with minimal configuration. Whether you're generating test data, creating demos, or building synthetic datasets, these generators provide the foundation for rapid, realistic data generation.
