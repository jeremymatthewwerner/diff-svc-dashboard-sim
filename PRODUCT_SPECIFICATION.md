# Customer Service Dashboard Simulation - Product Specification

## Overview
A web-based simulation system that automatically generates and manages customer service cases, providing real-time visibility into the simulated customer support operations. The system operates autonomously, with users able to observe but not control the simulation flow.

## Core Features

### 1. Case Display Dashboard
- Web-based user interface showing all customer service cases
- Cases displayed in a tabular format with one row per case
- Sorting: Most recent cases appear at the top
- Real-time updates as new cases are created or status changes

### 2. Case Information Display
Each case in the table will include:
- Case ID (unique identifier)
- Customer name
- Case creation date/time
- Current status (e.g., Open, In Progress, Resolved)
- Priority level
- Brief description/subject
- Assigned agent
- Last update timestamp

### 3. Simulation Engine
- Automated case generation averaging one new case every 15 seconds
- Pseudo-random distribution of case creation times
- Automatic status updates and progression of cases
- Simulated case resolution and closure
- Automated agent assignment and handling
- Configurable SLO failure rate (default 20%)
  - Controls probability of stages exceeding their SLO
  - When succeeding: targets 70% of SLO time
  - When failing: targets 120% of SLO time
  - Uses normal distribution for natural variation

#### Stage Transition Timing
- Each stage transition follows a normal (Gaussian) distribution
- Maximum average transition time of 30 seconds for any stage
- Standard deviation determined by the simulation engine
- Actual transition times are independent of configured SLO times
- SLOs from configuration are used for performance tracking only

#### Configuration Files

##### Stages.csv
- Defines the lifecycle stages of a case and their SLOs
- First row contains column headers: STAGE followed by stage names
- Stage progression order: WAITING → DEFINING → SOLVING → TRANSFERRING → RESOLVING → FOLLOWING-UP → CLOSED
- Subsequent rows contain priority-based SLOs (in seconds) for each stage
- First column of each row after header contains the priority level
- Each cell represents the SLO time in seconds for that priority-stage combination

##### Priorities.csv
- Single column CSV file defining valid priority levels
- Header row contains 'PRIORITY'
- Values range from 0 (lowest) to 10 (highest)
- Priority levels are referenced in Stages.csv for SLO definitions

### 4. Case Viewing
- Read-only access to case information
- Real-time observation of case progression
- Historical case viewing
- Case timeline tracking

### 5. User Interface Requirements

#### Statistics Display
- Centered box at top of window showing:
  - SLO failure rate control (0-100%)
  - Total case count since simulation start
  - Label: "Cases Created"

#### Stage Performance Metrics
- Each stage column header displays SLO performance:
  - Green percentage: Cases completed within SLO
  - Red percentage: Cases that exceeded SLO
  - Updates in real-time as cases progress
  - Format: "In SLO: [green]XX% | [red]YY%"

#### Case Tracking Table
- One row per case, sorted by creation time (newest first)
- Left-side case identifiers:
  - Creation timestamp displayed as an oval chip
  - Priority level (0-10) displayed as an oval chip

#### Stage Duration Columns
- One column for each stage (WAITING through CLOSED)
- Column headers show "Elapsed / SLO" to indicate time format
- All cells display time in format: "X / Y"
  - X: Current or final time spent in stage (Elapsed)
  - Y: SLO time allowed for the stage (SLO)

##### Active Stage Display
- Real-time counter showing elapsed seconds
- Updates continuously
- Background color changes dynamically:
  - Light green (#c8e6c9): Currently within SLO
  - Light red (#ffcdd2): Currently exceeding SLO

##### Completed Stage Display
- Shows final duration and SLO time
- Background color indicates final SLO status:
  - Dark green (#2e7d32): Completed under SLO time
  - Dark red (#c62828): Exceeded SLO time
- White text for better contrast on dark backgrounds

#### General UI Requirements
- Clean, modern web interface
- Fixed position header elements:
  - Statistics display area remains at top of page
  - Table header row stays visible while scrolling
- SLO failure rate input:
  - No scroll bars on number input
  - Clean, minimal appearance
- Responsive design for various screen sizes
- Easy-to-read table format
- Clear status indicators
- Intuitive navigation
- Real-time updates without page refresh

### 6. Data Storage
- Persistent storage of all case information
- Historical case data retention
- Secure data handling

## Technical Requirements

### Frontend
- Modern web framework
- Interactive table with sorting capabilities
- Real-time updates
- Responsive design

### Backend
- RESTful API architecture
- Database for case storage
- Data validation and sanitization
- Simulation state management
- Case generation engine
- Time-based event processing

## Future Enhancements (Phase 2)
- Advanced filtering and search capabilities
- Export functionality
- Analytics dashboard
- Customer communication integration
- SLA tracking and alerts

## Success Metrics
- System response time under 2 seconds
- Ability to handle 1000+ cases
- 99.9% uptime
- All case updates reflected in real-time
