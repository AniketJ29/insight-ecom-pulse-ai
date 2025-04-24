
import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { SalesChart } from "@/components/dashboard/SalesChart";
import { AiInsights } from "@/components/dashboard/AiInsights";
import { ProductsTable } from "@/components/dashboard/ProductsTable";
import { OrdersTable } from "@/components/dashboard/OrdersTable";
import { dashboardApi, DashboardStats } from "@/services/api";
import { BarChart3, Package, ShoppingBag, Users } from "lucide-react";

const Index = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      setIsLoading(true);
      try {
        const response = await dashboardApi.getStats();
        if (response.success && response.data) {
          setStats(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <DashboardLayout>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Revenue"
          value={stats ? formatCurrency(stats.totalSales) : "..."}
          description="Overall store revenue"
          icon={BarChart3}
          trend={stats?.revenueGrowth}
          isLoading={isLoading}
        />
        <StatCard
          title="Orders"
          value={stats?.totalOrders ?? "..."}
          description="Total number of orders"
          icon={ShoppingBag}
          trend={4.3}
          isLoading={isLoading}
        />
        <StatCard
          title="Customers"
          value={stats?.totalCustomers ?? "..."}
          description="Total registered customers"
          icon={Users}
          trend={2.1}
          isLoading={isLoading}
        />
        <StatCard
          title="Products"
          value={stats?.totalProducts ?? "..."}
          description="Active products in store"
          icon={Package}
          trend={-0.8}
          isLoading={isLoading}
        />
      </div>
      
      <div className="grid gap-4 mt-4">
        <SalesChart />
        <AiInsights />
        <ProductsTable />
        <OrdersTable />
      </div>
    </DashboardLayout>
  );
};

export default Index;
