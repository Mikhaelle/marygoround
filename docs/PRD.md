# MeryGoRound - Product Requirements Document

## 1. Vision

MeryGoRound is a web application that gamifies household chores through a spinning wheel mechanic, making mundane tasks fun and fair. It also manages "adult life" responsibilities through a structured bucket system that ensures important tasks don't get neglected.

## 2. Target Users

- Individuals and households who want to distribute and gamify daily chores
- People who need accountability for adult responsibilities (scheduling appointments, paying bills)
- Multi-user households where fairness in task distribution matters

## 3. Core Features

### 3.1 Spinning Wheel (Roda Giratoria)

**Description**: An animated spinning wheel that randomly selects a household chore for the user to complete.

**Requirements**:
- Visual spinning wheel rendered on HTML5 Canvas
- Each chore appears as a segment on the wheel
- Segment size is proportional to the chore's effective weight
- Spin animation with realistic deceleration (ease-out cubic)
- Result is determined server-side to prevent manipulation
- After spin, user can mark the task as completed or skip

**Chore Properties**:
- Name (required, text)
- Estimated duration: 1-10 minutes (required)
- Category (optional, for organization)
- Multiplicity: how many times the chore appears on the wheel (default: 1)
- Time-based weight rules: increase probability at specific hours

### 3.2 Chore Management (CRUD)

**Description**: Full management of chore items that appear on the spinning wheel.

**Requirements**:
- Create new chores with all properties
- Edit existing chores (name, duration, category, multiplicity, time weights)
- Delete chores (with confirmation)
- List all chores with search/filter
- Time weight editor: visual grid of 24 hours where users set weight per hour
- Default time weight is 1.0 (neutral) for unconfigured hours

### 3.3 Time-Based Probability

**Description**: Some chores have higher chances of being selected at certain times of day.

**Requirements**:
- Each chore can have weight rules for specific hours (0-23)
- Weight is a positive float multiplier (e.g., 2.0 = double chance)
- Effective weight = multiplicity x time_weight_for_current_hour
- If no rule matches current hour, weight defaults to 1.0
- Example: "Lavar pratos" (wash dishes) has weight 3.0 at hours 12 and 19

### 3.4 Adult Life Bucket (Balde de Vida Adulta)

**Description**: A separate system for important adult tasks that need to be resolved but aren't daily chores.

**Requirements**:
- Separate CRUD for bucket items (name, description, category)
- Draw mechanism: randomly selects 1 item from the bucket
- One-at-a-time rule: user can only have 1 active drawn item
- To draw a new item, user must either:
  - Resolve the current item (mark as done)
  - Return it with a written justification (minimum 10 characters)
- Resolved items are permanently removed from the draw pool
- Returned items go back to the pool for future draws
- Active draw is prominently displayed on the bucket page

**Example bucket items**:
- Schedule annual doctor checkup
- Renew driver's license
- Organize tax documents
- Update emergency contacts
- Review insurance policies

### 3.5 Push Notifications

**Description**: Browser push notifications that remind users to spin the wheel.

**Requirements**:
- Browser Push Notification via Web Push API + Service Worker
- Works even when browser tab is closed
- Default interval: every 1 hour
- Configurable interval (30 min, 1 hour, 2 hours)
- Quiet hours: user can set hours during which no notifications are sent
- Enable/disable toggle
- Notification message: "Time to spin the wheel!" with link to app

### 3.6 Authentication

**Description**: Multi-user system with email/password authentication.

**Requirements**:
- Register with email, password, and name
- Login with email and password
- JWT-based auth (access token + refresh token)
- Each user has their own chores, wheel config, and bucket
- Protected routes (redirect to login if unauthenticated)

### 3.7 Internationalization (i18n)

**Description**: Support for Portuguese (PT-BR) and English.

**Requirements**:
- All UI text available in both languages
- Language auto-detected from browser settings
- Manual language switcher in settings
- PT-BR as primary language

## 4. Non-Functional Requirements

### 4.1 Performance
- Wheel spin animation: smooth 60fps
- API response time: < 200ms for all endpoints
- Frontend initial load: < 3s

### 4.2 Security
- Passwords hashed with bcrypt
- JWT with short-lived access tokens (15 min)
- CORS configured for frontend origin only
- Input validation on all endpoints (Pydantic)
- Rate limiting on auth endpoints

### 4.3 Reliability
- Database with persistent Docker volumes
- Graceful error handling with user-friendly messages
- Service health checks in Docker

### 4.4 Accessibility
- Keyboard navigable wheel (space to spin)
- ARIA labels on interactive elements
- Color-blind friendly segment colors
- Responsive design (mobile-first)

## 5. Technical Architecture

See CLAUDE.md for detailed technical specifications.

## 6. Data Model

### Users
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | string | Unique, login identifier |
| name | string | Display name |
| hashed_password | string | bcrypt hash |

### Chores
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner |
| name | string | Chore name |
| estimated_duration_minutes | int | 1-10 |
| category | string? | Optional grouping |

### Wheel Configuration
| Field | Type | Description |
|-------|------|-------------|
| chore_id | UUID | Parent chore |
| multiplicity | int | Times on wheel (>=1) |
| time_weight_rules | JSON | [{hour, weight}] |

### Bucket Items
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner |
| name | string | Task name |
| description | string? | Details |

### Bucket Draws
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| bucket_item_id | UUID | Drawn item |
| user_id | UUID | User who drew |
| status | enum | ACTIVE/RESOLVED/RETURNED |
| return_justification | string? | Required if RETURNED |

## 7. Success Metrics

- Users spin the wheel at least 3x per day
- 80% of spun chores are marked as completed
- Active bucket items are resolved within 7 days on average
- Notification opt-in rate > 60%
