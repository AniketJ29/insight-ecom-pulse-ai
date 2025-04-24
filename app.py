
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import os
import json
from datetime import datetime, timedelta
import random
from bson import json_util

app = Flask(__name__)
CORS(app)

# MongoDB connection
# Replace with your MongoDB connection string
MONGO_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/ecom"

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client.ecom  # Use the ecom database
    print("Connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Helper function to parse MongoDB results to JSON
def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        # Get total sales
        sales_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
        sales_result = list(db.sales.aggregate(sales_pipeline))
        total_sales = sales_result[0]["total"] if sales_result else 0
        
        # Get total customers
        total_customers = db.customer.count_documents({})
        
        # Get total orders
        total_orders = db.order.count_documents({})
        
        # Get total products
        total_products = db.product.count_documents({})
        
        # Calculate revenue growth (comparing current month to previous month)
        current_date = datetime.now()
        first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_day_prev_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
        
        current_month_sales = db.sales.aggregate([
            {"$match": {"date": {"$gte": first_day_current_month}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        current_month_total = list(current_month_sales)[0]["total"] if list(current_month_sales) else 0
        
        prev_month_sales = db.sales.aggregate([
            {"$match": {"date": {"$gte": first_day_prev_month, "$lt": first_day_current_month}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        prev_month_total = list(prev_month_sales)[0]["total"] if list(prev_month_sales) else 1  # Avoid division by zero
        
        revenue_growth = ((current_month_total - prev_month_total) / prev_month_total) * 100
        
        # Calculate average order value
        avg_order_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$total"}}}]
        avg_order_result = list(db.order.aggregate(avg_order_pipeline))
        avg_order_value = avg_order_result[0]["avg"] if avg_order_result else 0
        
        return jsonify({
            "success": True,
            "data": {
                "totalSales": total_sales,
                "totalCustomers": total_customers,
                "totalOrders": total_orders,
                "totalProducts": total_products,
                "revenueGrowth": revenue_growth,
                "averageOrderValue": avg_order_value
            }
        })
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/sales-time-series', methods=['GET'])
def get_sales_time_series():
    try:
        period = request.args.get('period', '30d')
        
        # Calculate date range based on period
        end_date = datetime.now()
        
        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        elif period == '365d':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        # Group by day for the specified period
        pipeline = [
            {"$match": {"date": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                "value": {"$sum": "$amount"}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        results = list(db.sales.aggregate(pipeline))
        
        # Format the results
        time_series_data = []
        for item in results:
            time_series_data.append({
                "date": item["_id"],
                "value": item["value"]
            })
        
        return jsonify({"success": True, "data": time_series_data})
    except Exception as e:
        print(f"Error fetching sales time series: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/products', methods=['GET'])
def get_products():
    try:
        limit = int(request.args.get('limit', 10))
        sort = request.args.get('sort', 'sales')
        
        # Get products with their sales count
        pipeline = [
            {"$lookup": {
                "from": "order",
                "localField": "_id",
                "foreignField": "products.product_id",
                "as": "orders"
            }},
            {"$addFields": {
                "sales": {"$size": "$orders"}
            }},
            {"$project": {
                "name": 1,
                "price": 1,
                "stock": 1,
                "category": 1,
                "sales": 1
            }},
            {"$sort": {sort: -1}},
            {"$limit": limit}
        ]
        
        products = list(db.product.aggregate(pipeline))
        
        # Format the results
        formatted_products = []
        for product in products:
            formatted_products.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "price": product["price"],
                "stock": product["stock"],
                "category": product["category"],
                "sales": product["sales"]
            })
        
        return jsonify({"success": True, "data": formatted_products})
    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/orders', methods=['GET'])
def get_orders():
    try:
        limit = int(request.args.get('limit', 10))
        sort = request.args.get('sort', 'date')
        order = request.args.get('order', 'desc')
        
        sort_direction = -1 if order == 'desc' else 1
        
        # Get the most recent orders
        pipeline = [
            {"$lookup": {
                "from": "customer",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer"
            }},
            {"$unwind": "$customer"},
            {"$project": {
                "date": 1,
                "total": 1,
                "status": 1,
                "items": {"$size": "$products"},
                "customerName": "$customer.name",
                "customerId": "$customer._id"
            }},
            {"$sort": {sort: sort_direction}},
            {"$limit": limit}
        ]
        
        orders = list(db.order.aggregate(pipeline))
        
        # Format the results
        formatted_orders = []
        for order in orders:
            formatted_orders.append({
                "id": str(order["_id"]),
                "customerId": str(order["customerId"]),
                "customerName": order["customerName"],
                "date": order["date"].isoformat(),
                "total": order["total"],
                "status": order["status"],
                "items": order["items"]
            })
        
        return jsonify({"success": True, "data": formatted_orders})
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/ai-insights', methods=['GET'])
def get_ai_insights():
    try:
        count = int(request.args.get('count', 3))
        
        # This is where you would integrate with Llama 3.2
        # For now, we'll return placeholder insights based on real data
        
        # Get some actual statistics to base insights on
        low_stock_count = db.product.count_documents({"stock": {"$lt": 10}})
        
        # Top performing category
        category_pipeline = [
            {"$lookup": {
                "from": "order",
                "localField": "_id",
                "foreignField": "products.product_id",
                "as": "orders"
            }},
            {"$addFields": {"sales": {"$size": "$orders"}}},
            {"$group": {
                "_id": "$category",
                "totalSales": {"$sum": "$sales"}
            }},
            {"$sort": {"totalSales": -1}},
            {"$limit": 1}
        ]
        top_category_result = list(db.product.aggregate(category_pipeline))
        top_category = top_category_result[0]["_id"] if top_category_result else "N/A"
        
        # Customer retention
        repeat_customers_pipeline = [
            {"$group": {
                "_id": "$customer_id",
                "orderCount": {"$sum": 1}
            }},
            {"$match": {"orderCount": {"$gt": 1}}},
            {"$count": "count"}
        ]
        repeat_customers_result = list(db.order.aggregate(repeat_customers_pipeline))
        repeat_customers = repeat_customers_result[0]["count"] if repeat_customers_result else 0
        total_customers = db.customer.count_documents({})
        retention_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Create insights based on actual data
        insights = [
            {
                "type": "inventory",
                "title": f"{low_stock_count} Products Low in Stock",
                "description": f"You currently have {low_stock_count} products with inventory below 10 units.",
                "recommendation": "Consider restocking these items soon to avoid stockouts and lost sales.",
                "confidence": 0.95
            },
            {
                "type": "sales",
                "title": f"{top_category} is Your Top Performing Category",
                "description": f"Products in the {top_category} category are generating the most sales.",
                "recommendation": "Consider expanding your product line in this category or running promotions to boost sales further.",
                "confidence": 0.9
            },
            {
                "type": "customers",
                "title": f"{retention_rate:.1f}% Customer Retention Rate",
                "description": f"Your repeat customer rate is {retention_rate:.1f}%. This is the percentage of customers who have made more than one purchase.",
                "recommendation": "Implement a loyalty program to increase customer retention and lifetime value.",
                "confidence": 0.85
            }
        ]
        
        # Limit to requested count
        insights = insights[:count]
        
        return jsonify({"success": True, "data": insights})
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/customers', methods=['GET'])
def get_customers():
    try:
        limit = int(request.args.get('limit', 10))
        sort = request.args.get('sort', 'totalSpent')
        
        # Get customers with their order statistics
        pipeline = [
            {"$lookup": {
                "from": "order",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "orders"
            }},
            {"$addFields": {
                "totalOrders": {"$size": "$orders"},
                "totalSpent": {"$sum": "$orders.total"},
                "lastOrderDate": {"$max": "$orders.date"}
            }},
            {"$sort": {sort: -1}},
            {"$limit": limit}
        ]
        
        customers = list(db.customer.aggregate(pipeline))
        
        # Format the results
        formatted_customers = []
        for customer in customers:
            formatted_customers.append({
                "id": str(customer["_id"]),
                "name": customer["name"],
                "email": customer["email"],
                "totalOrders": customer["totalOrders"],
                "totalSpent": customer["totalSpent"],
                "lastOrderDate": customer["lastOrderDate"].isoformat() if "lastOrderDate" in customer else None
            })
        
        return jsonify({"success": True, "data": formatted_customers})
    except Exception as e:
        print(f"Error fetching customers: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
