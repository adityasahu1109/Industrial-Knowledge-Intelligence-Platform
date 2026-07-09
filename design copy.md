# BHEL Quality Management Dashboard — Frontend Design & Architecture

---

## 1. Overview

The **BHEL Quality Management Dashboard (QIS)** is a React-based single-page application built to monitor acceptance rates, rejections, vendor performance, and quality analytics. It serves as an intranet portal for quality control officers, providing data-dense, live monitoring and exploration capabilities.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Framework | React 19 (JSX) |
| Build Tool | Vite |
| Routing | React Router DOM v7 |
| State Management | React Context (`AuthContext`) |
| Styling | Tailwind CSS (via `@import`) + Custom CSS (`index.css`) |
| Icons | Lucide React |

---

## 3. Design Philosophy & Aesthetics

The application uses an industrial, data-centric design language optimized for readability and high information density. 

1. **Brand Identity:** Heavily utilizes the corporate BHEL Navy Blue (`#002A54`) for branding, sidebars, and primary accents.
2. **Clean Data Presentation:** Uses white cards (`#ffffff`) on a light slate background (`#f1f5f9`) to create clear separation of information domains.
3. **Responsive Grid Architecture:** Employs a robust, CSS-native responsive grid system designed to scale gracefully from 1024px monitors up to 4K displays.
4. **Subtle Motion:** Uses lightweight CSS animations (fade-ins, slide-ups) to make data loading feel fluid without being distracting.

---

## 4. Color System

The color palette leans into professional, muted slate tones with sharp, meaningful accents.

| Color | Hex Code | Usage |
|---|---|---|
| **BHEL Navy** | `#002A54` | Sidebar background, primary buttons, active focus rings |
| **Page Background** | `#f1f5f9` | Main content area backdrop |
| **Card Surface** | `#ffffff` | Elevated data containers |
| **Primary Text** | `#0f172a` | Headings, emphasized data |
| **Secondary Text** | `#334155` | Standard body copy |
| **Muted Text** | `#94a3b8` | Placeholders, timestamps, secondary labels |
| **Border** | `#e2e8f0` | Dividers, subtle card borders |
| **Success (Live)** | `#22c55e` | Live status indicators, positive trends |
| **Error / Alert** | `#dc2626` | Rejections, notifications badge, logout action |

---

## 5. Layout Architecture

The application uses a standard enterprise dashboard shell, implemented in `MainLayout.jsx`.

```
┌────────────────────────────────────────────────────────┐
│             │ <TopBar> h-64px                          │
│  <Sidebar>  │ ──────────────────────────────────────── │
│  w-256px    │ Title | Unified Search | Bell | User Profile
│  (Fixed)    │                                          │
│             │ <main> (Flex-1)                          │
│  BHEL QIS   │ ┌──────────────────────────────────────┐ │
│  Brand      │ │  Dashboard / Page Content            │ │
│             │ │  (.main-content padding: 28px 32px)  │ │
│  Accordion  │ └──────────────────────────────────────┘ │
│  Nav        │                                          │
│             │ <Footer>                                 │
└─────────────┴──────────────────────────────────────────┘
```

### 5.1 Sidebar (`Sidebar.jsx`)
- **Width:** Fixed to `var(--sidebar-w)` (256px on desktop, collapses to 220px on smaller screens).
- **Styling:** Solid BHEL Navy (`#002A54`) background with white text.
- **Navigation:** Deeply nested accordion menu for "Core Analytics", "Quality Applications", "Call Booking", and "Corporate Guidelines".
- **Interaction:** Hover states use subtle white translucency (`rgba(255,255,255,0.07)`). Active states highlight with `rgba(255,255,255,0.13)`.

### 5.2 TopBar (`TopBar.jsx`)
- **Height:** Sticky 64px header.
- **Left:** Dynamic page title and current localized date.
- **Right:** 
  - **Unified Search:** A multi-modal search input that allows searching by Vendor Name, Vendor ID, GRN Number, or Part Number. Features a dropdown context-switcher and live search recommendations.
  - **Notifications:** Dropdown panel showing mock alerts (e.g., "New GRN Uploaded").
  - **User Context:** Name and Role display.
  - **Logout:** Action button highlighted in red.

---

## 6. CSS Architecture & Utilities

The project relies heavily on `index.css` for structural utilities rather than inline Tailwind classes for layout grids.

### 6.1 Responsive Grids
Custom grid classes handle responsive column collapse automatically based on breakpoints:
- `.r-grid-4`: 4 columns on large, 2 columns on medium, 1 on small.
- `.r-grid-3`: 3 columns on large, 2 columns on medium, 1 on small.
- `.r-grid-2`: 2 columns on large, 1 column on small.

### 6.2 UI Utilities
- `.card`: Standardized container (`bg-white`, `border-slate-200`, `rounded-12px`, soft shadow).
- `.dash-stack`: Vertical flex container with responsive gaps (`22px` standard).
- **Animations:** `.animate-fade-in`, `.animate-slide-up`, and stagger classes (`.stagger-1` through `.stagger-6`) for cascading load effects.
- **Form Elements:** Global resets for `input[type="text"]`, `select`, etc., enforcing a consistent 8px radius and slate borders.
- **Scrollbar:** Custom 6px minimalist scrollbar to maintain a clean UI.

---

## 7. Routing & Page Structure

| Route Path | Component | Purpose |
|---|---|---|
| `/` | `DashboardPage.jsx` | High-level analytics overview with month/year filters and KPI charts. |
| `/explore` | `ExplorePage.jsx` | Deep dive tabular data exploration and analytics. |
| `/vendor/:vendorName`| `VendorPage.jsx` | Dynamic, detailed performance profile for a specific supplier. |
| `/compare` | `CompareVendorsPage.jsx`| Side-by-side metric comparison of multiple vendors. |
| `/part/:id` | `PartPage.jsx` | Quality metrics and history for a specific material/part code. |
| `/grn/:grnNumber` | `GRNPage.jsx` | Deep dive into a specific Goods Receipt Note transaction. |
| `/*` (Various) | `PlaceholderPage.jsx` | Stubs for Quality Policy, ISO docs, NCR, PMDR, and other apps. |

---

## 8. Dashboard Breakdown (`DashboardPage.jsx`)

The primary view of the application features:
1. **Header Banner:** Shows active month selection (e.g., "Overview for March 2024") and "Live 24h monitoring" badge. Includes custom styled `<select>` dropdowns for Year and Month.
2. **Stat Cards (Row 1):** Uses `.r-grid-4` to display 4 high-level KPI cards (loaded via `StatCard` component).
3. **Charts (Row 2):** Uses `.r-grid-2`. Contains `AcceptanceChart` (trend lines) and `VendorPerformance` (bar/scatter).
4. **Charts (Row 3):** Uses `.r-grid-2`. Contains `RejectionPie` (composition) and `AcceptanceByItemChart` (distribution).
5. **Loading States:** Uses a dedicated `CardSkeleton` component (`components/ui/Skeleton.jsx`) to pulse smoothly while data fetches via the API.

---

## 9. Design Patterns

- **Data Fetching:** Standardized pattern using `useEffect`, cleanup functions to prevent state updates on unmounted components, and dedicated `loading`/`error` states.
- **Error Handling:** `ErrorBox.jsx` provides a consistent UI for API failures with a "Retry" mechanism.
- **Click-away Listeners:** Used extensively in `TopBar.jsx` for search suggestions and notification dropdowns using `useRef` and `mousedown` event listeners.
- **Data Densification:** Small fonts (`10px` to `13px`) are used intentionally to fit high volumes of industrial data on single screens without requiring excessive scrolling.
