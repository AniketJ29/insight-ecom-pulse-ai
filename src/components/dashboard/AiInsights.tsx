
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { dashboardApi, AiInsight } from "@/services/api";
import { Brain, Sparkles, TrendingUp } from "lucide-react";

export function AiInsights() {
  const [insights, setInsights] = useState<AiInsight[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function fetchInsights() {
      setIsLoading(true);
      try {
        const response = await dashboardApi.getAiInsights();
        if (response.success && response.data) {
          setInsights(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch AI insights:", error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchInsights();
  }, []);

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-insight-teal" /> AI Insights
          </CardTitle>
          <CardDescription>Powered by Llama 3.2</CardDescription>
        </div>
        <Sparkles className="h-5 w-5 text-insight-blue" />
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-32 rounded-lg animate-pulse bg-muted"></div>
            ))}
          </div>
        ) : insights.length > 0 ? (
          <>
            {insights.map((insight, index) => (
              <div key={index} className="insight-card">
                <div className="flex justify-between items-start">
                  <h3 className="font-semibold text-lg">{insight.title}</h3>
                  {insight.confidence && (
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                      {Math.round(insight.confidence * 100)}% confidence
                    </span>
                  )}
                </div>
                <p className="text-sm mt-2 text-muted-foreground">{insight.description}</p>
                {insight.recommendation && (
                  <div className="mt-4 border-t border-insight-teal/20 pt-3">
                    <p className="text-sm font-medium flex items-center gap-1">
                      <TrendingUp className="h-4 w-4 text-insight-teal" />
                      Recommendation:
                    </p>
                    <p className="text-sm mt-1">{insight.recommendation}</p>
                  </div>
                )}
              </div>
            ))}
          </>
        ) : (
          <div className="text-center p-8">
            <p className="text-muted-foreground">No insights available currently</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
