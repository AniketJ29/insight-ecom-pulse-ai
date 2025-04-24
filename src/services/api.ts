
import { toast } from "../components/ui/use-toast";

const API_URL = "http://localhost:5000/api";

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Function to handle API errors
const handleApiError = (error: any): never => {
  const errorMessage = error.message || "An unknown error occurred";
  toast({
    variant: "destructive",
    title: "API Error",
    description: errorMessage,
  });
  throw error;
};

// Generic fetch function
async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers || {}),
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Error ${response.status}`);
    }

    return { success: true, data: data as T };
  } catch (error: any) {
    console.error(`API Error (${endpoint}):`, error);
    return { success: false, error: error.message };
  }
}

// Dashboard Data
export interface DashboardStats {
  totalSales: number;
  totalCustomers: number;
  totalOrders: number;
  totalProducts: number;
  revenueGrowth: number;
  averageOrderValue: number;
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface ProductData {
  id: string;
  name: string;
  price: number;
  stock: number;
  category: string;
  sales: number;
}

export interface CustomerData {
  id: string;
  name: string;
  email: string;
  totalOrders: number;
  totalSpent: number;
  lastOrderDate: string;
}

export interface OrderData {
  id: string;
  customerId: string;
  customerName: string;
  date: string;
  total: number;
  status: string;
  items: number;
}

export interface AiInsight {
  type: string;
  title: string;
  description: string;
  recommendation?: string;
  relatedMetric?: string;
  confidence?: number;
}

// Dashboard API
export const dashboardApi = {
  // Get key metrics
  getStats: () => fetchApi<DashboardStats>("/dashboard/stats"),
  
  // Get sales time series data
  getSalesTimeSeries: (period: string = "30d") => 
    fetchApi<TimeSeriesData[]>(`/dashboard/sales-time-series?period=${period}`),
  
  // Get products data
  getProducts: (limit: number = 10, sort: string = "sales") =>
    fetchApi<ProductData[]>(`/dashboard/products?limit=${limit}&sort=${sort}`),
  
  // Get customers data
  getCustomers: (limit: number = 10, sort: string = "totalSpent") =>
    fetchApi<CustomerData[]>(`/dashboard/customers?limit=${limit}&sort=${sort}`),
  
  // Get orders data
  getOrders: (limit: number = 10, sort: string = "date", order: string = "desc") =>
    fetchApi<OrderData[]>(`/dashboard/orders?limit=${limit}&sort=${sort}&order=${order}`),

  // Get AI insights
  getAiInsights: (count: number = 3) =>
    fetchApi<AiInsight[]>(`/dashboard/ai-insights?count=${count}`),
};
