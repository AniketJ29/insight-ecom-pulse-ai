
# InsightEcom Pulse AI - E-commerce Analytics Dashboard

Real-time e-commerce analytics dashboard with MongoDB and Llama 3.2 AI insights.

## Frontend (React + TypeScript)

- Built with React, TypeScript, Tailwind CSS, and Shadcn UI
- Real-time data visualization with Recharts
- Responsive design for all devices

## Backend (Flask + MongoDB)

- Flask API endpoints for analytics data
- MongoDB integration for real data access
- Llama 3.2 AI integration for intelligent insights

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.8+
- MongoDB Atlas account

### Installation

1. Clone the repository

2. Install frontend dependencies
```
npm install
```

3. Install backend dependencies
```
pip install -r requirements.txt
```

4. Configure MongoDB connection
   - Copy `.env.example` to `.env`
   - Add your MongoDB connection string

5. Start the backend server
```
python app.py
```

6. Start the frontend development server
```
npm run dev
```

7. Visit `http://localhost:5173` in your browser

## MongoDB Collections

The application uses the following collections in the `ecom` database:
- `admin` - Admin user information
- `sales` - Sales transactions
- `customer` - Customer information
- `product` - Product catalog
- `order` - Order details

## Llama 3.2 Integration

The AI insights feature uses Llama 3.2 to analyze MongoDB data and provide actionable recommendations.

