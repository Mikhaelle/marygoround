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
- Each chore appears as a segment on the wheel, with text displayed horizontally along the segment
- Segment size is proportional to the chore's effective weight
- Spin animation with realistic deceleration (ease-out cubic, ~4.5s duration)
- Result is determined server-side to prevent manipulation
- After spin, user can mark the task as completed or skip
- Completed chores are removed from the wheel for the rest of the day
- Wheel resets daily: all chores return at midnight

**Daily Reset Behavior**:
- Each chore with multiplicity N has N "slots" on the wheel
- Completing a chore removes 1 slot (e.g., multiplicity 4, completed 1x = 3 remaining slots)
- When all slots are used (completions >= multiplicity), the chore disappears from the wheel
- At midnight (UTC), all completion counts reset and the wheel is fully restored

**Chore Properties**:
- Name (required, text)
- Estimated duration: 5 or 10 minutes (required, discrete options)
- Category (optional, for organization)
- Multiplicity: how many slots the chore occupies on the wheel (>= 1, no upper limit)
- Time-based weight rules: increase probability at specific hours (max weight: 3.0)

### 3.2 Chore Management (CRUD)

**Description**: Full management of chore items that appear on the spinning wheel.

**Requirements**:
- Create new chores with all properties
- Edit existing chores (name, duration, category, multiplicity, time weights)
- Delete chores (with confirmation)
- List all chores with search/filter
- Duration selector: two buttons (5 min / 10 min)
- Multiplicity: free numeric input (>= 1)
- Time weight editor: visual 24-hour grid with bar chart per hour, max weight 3.0
- Default time weight is 1.0 (neutral) for unconfigured hours

### 3.3 Time-Based Probability

**Description**: Some chores have higher chances of being selected at certain times of day.

**Requirements**:
- Each chore can have weight rules for specific hours (0-23)
- Weight is a positive float multiplier, maximum 3.0
- Effective weight = multiplicity x time_weight_for_current_hour
- If no rule matches current hour, weight defaults to 1.0
- Example: "Lavar louca" (wash dishes) has weight 3.0 at hours 19-22

### 3.4 Adult Life Bucket (Balde de Vida Adulta)

**Description**: A separate system for important adult tasks that need to be resolved but aren't daily chores. These are things like scheduling doctor appointments, renewing documents, organizing finances.

**Requirements**:
- Separate CRUD for bucket items (name, description, category)
- Draw mechanism: randomly selects 1 item from the bucket
- One-at-a-time rule: user can only have 1 active drawn item (enforced at database level with partial unique index)
- To draw a new item, user must either:
  - Resolve the current item (mark as done)
  - Return it with a written justification (minimum 10 characters)
- Resolved items are permanently removed from the draw pool
- Returned items go back to the pool for future draws
- Active draw is prominently displayed on the bucket page

**Example bucket items**:
- Marcar consulta medica anual
- Renovar carteira de motorista
- Organizar documentos de imposto
- Atualizar contatos de emergencia
- Revisar apolices de seguro

### 3.5 Push Notifications

**Description**: Browser push notifications that remind users to spin the wheel.

**Requirements**:
- Browser Push Notification via Web Push API + Service Worker + VAPID
- Works even when browser tab is closed
- Default interval: every 1 hour
- Configurable interval (30 min, 1 hour, 2 hours)
- Quiet hours: user can set hours during which no notifications are sent
- Enable/disable toggle in Settings page (requests browser permission on enable)
- Service Worker auto-registered on dashboard load
- Backend scheduler (APScheduler) checks every minute and sends when due
- Supports multiple devices per user

### 3.6 Authentication

**Description**: Multi-user system with email/password authentication.

**Requirements**:
- Register with email, password, and name
- Login with email and password
- JWT-based auth (access token 15min + refresh token 7 days)
- Automatic token refresh on 401 responses
- Each user has their own chores, wheel config, and bucket
- Protected routes (redirect to login if unauthenticated)

### 3.7 Internationalization (i18n)

**Description**: Support for Portuguese (PT-BR) and English.

**Requirements**:
- All UI text available in both languages via next-intl
- Language auto-detected from browser settings
- Manual language switcher in Settings page
- PT-BR as primary language
- Code (variables, functions, commits) always in English

## 4. Non-Functional Requirements

### 4.1 Performance
- Wheel spin animation: smooth 60fps on Canvas
- API response time: < 200ms for all endpoints
- Frontend initial load: < 3s (Turbopack)

### 4.2 Security
- Passwords hashed with bcrypt (direct, not passlib)
- JWT with short-lived access tokens (15 min)
- CORS configured for frontend origin only
- Input validation on all endpoints (Pydantic v2)
- Partial unique index on bucket_draws for active draw constraint

### 4.3 Reliability
- Database with persistent Docker volumes
- Graceful error handling with domain exception to HTTP status mapping
- Service health checks in Docker (PostgreSQL, Redis, Backend)
- Hot reload in development (Uvicorn watchfiles + Next.js Turbopack)

### 4.4 Accessibility
- Keyboard navigable wheel (click center to spin)
- Responsive design (mobile-first with bottom nav, desktop with sidebar)
- Color-coded segments with text shadows for readability

## 5. Technical Architecture

### Stack
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy async + asyncpg + Alembic
- **Frontend**: Next.js 14+ (App Router) + React 19 + Tailwind CSS + shadcn/ui + next-intl
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Push**: pywebpush + Web Push API + Service Worker
- **Containers**: Docker + docker-compose
- **Formatters**: Ruff (Python), ESLint + Prettier (TypeScript)

### Architecture Pattern
Clean Architecture with DDD tactical patterns:
- **Domain Layer**: Entities, Value Objects, Repository ABCs, Domain Services (zero external dependencies)
- **Application Layer**: Use Cases (Commands/Queries), DTOs (depends only on domain)
- **Infrastructure Layer**: SQLAlchemy repos, JWT, bcrypt, pywebpush, APScheduler
- **API Layer**: FastAPI routes, dependency injection, middleware

### Bounded Contexts
1. **Identity**: User registration, authentication, JWT tokens
2. **Chores**: Chore CRUD with wheel configuration (multiplicity, time weights)
3. **Wheel**: Spinning logic, spin sessions, daily reset, segment calculation
4. **Adult Bucket**: Bucket items, draw system, resolve/return workflow
5. **Notification**: Push subscriptions, preferences, scheduled delivery

## 6. Data Model

### Users
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique, login identifier |
| name | VARCHAR(100) | Display name |
| hashed_password | VARCHAR(255) | bcrypt hash |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

### Chores
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| name | VARCHAR(200) | Chore name |
| estimated_duration_minutes | SMALLINT | 5 or 10 |
| category | VARCHAR(100) | Optional grouping |
| multiplicity | SMALLINT | Wheel slots (>= 1) |
| time_weight_rules | JSON | [{hour, weight}], weight <= 3.0 |
| created_at | TIMESTAMPTZ | Creation timestamp |
| updated_at | TIMESTAMPTZ | Last update timestamp |

### Spin Sessions
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| selected_chore_id | UUID | FK to chores |
| chore_name | VARCHAR(200) | Snapshot of chore name |
| spun_at | TIMESTAMPTZ | Spin timestamp |
| completed_at | TIMESTAMPTZ | Completion timestamp |
| status | VARCHAR(20) | pending/completed/skipped |

### Bucket Items
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| name | VARCHAR(200) | Task name |
| description | TEXT | Details |
| category | VARCHAR(100) | Optional grouping |

### Bucket Draws
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| bucket_item_id | UUID | FK to bucket_items |
| user_id | UUID | FK to users |
| drawn_at | TIMESTAMPTZ | Draw timestamp |
| status | VARCHAR(20) | active/resolved/returned |
| resolved_at | TIMESTAMPTZ | Resolution timestamp |
| return_justification | TEXT | Required if returned (min 10 chars) |
| | PARTIAL UNIQUE INDEX | (user_id) WHERE status='active' |

### Push Subscriptions
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users |
| endpoint | TEXT | Push service endpoint (unique) |
| p256dh_key | TEXT | Client public key |
| auth_key | TEXT | Authentication secret |

### Notification Preferences
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users (unique) |
| interval_minutes | SMALLINT | Default 60 |
| enabled | BOOLEAN | Default false |
| quiet_hours_start | SMALLINT | Hour 0-23 |
| quiet_hours_end | SMALLINT | Hour 0-23 |
| last_notified_at | TIMESTAMPTZ | Last push sent |

## 7. API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/refresh | Refresh tokens |
| GET | /api/v1/auth/me | Get current user |

### Chores
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/chores | List user chores |
| POST | /api/v1/chores | Create chore |
| GET | /api/v1/chores/{id} | Get chore |
| PUT | /api/v1/chores/{id} | Update chore |
| DELETE | /api/v1/chores/{id} | Delete chore |

### Wheel
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/wheel/spin | Spin the wheel |
| PUT | /api/v1/wheel/sessions/{id}/complete | Mark completed |
| PUT | /api/v1/wheel/sessions/{id}/skip | Skip chore |
| GET | /api/v1/wheel/history | Paginated history |
| GET | /api/v1/wheel/segments | Current segments with weights |

### Bucket
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/bucket/items | List bucket items |
| POST | /api/v1/bucket/items | Create item |
| PUT | /api/v1/bucket/items/{id} | Update item |
| DELETE | /api/v1/bucket/items/{id} | Delete item |
| POST | /api/v1/bucket/draw | Draw from bucket |
| GET | /api/v1/bucket/draws/active | Get active draw |
| PUT | /api/v1/bucket/draws/{id}/resolve | Resolve draw |
| PUT | /api/v1/bucket/draws/{id}/return | Return with justification |

### Notifications
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/notifications/subscribe | Register push subscription |
| DELETE | /api/v1/notifications/unsubscribe | Remove all subscriptions |
| GET | /api/v1/notifications/preferences | Get preferences |
| PUT | /api/v1/notifications/preferences | Update preferences |

## 8. Success Metrics

- Users spin the wheel at least 3x per day
- 80% of spun chores are marked as completed
- Active bucket items are resolved within 7 days on average
- Notification opt-in rate > 60%
