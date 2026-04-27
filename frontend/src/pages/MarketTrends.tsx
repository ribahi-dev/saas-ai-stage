import { useEffect, useState } from 'react';
import { ChartBarIcon, FireIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

interface SkillTrend {
  skill: string;
  count: number;
  percentage: number;
}

interface CityTrend {
  city: string;
  count: number;
}

interface PlatformTrend {
  platform: string;
  count: number;
}

interface MarketTrendsResponse {
  total_offers_analyzed: number;
  top_skills: SkillTrend[];
  top_cities: CityTrend[];
  top_platforms: PlatformTrend[];
}

export default function MarketTrendsPage() {
  const [data, setData] = useState<MarketTrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/ai/market-trends/')
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const maxCount = data?.top_skills[0]?.count || 1;

  const getBarColor = (idx: number) => {
    const colors = [
      'from-red-500 to-orange-400',
      'from-orange-500 to-yellow-400',
      'from-yellow-500 to-lime-400',
      'from-green-500 to-emerald-400',
      'from-teal-500 to-cyan-400',
      'from-cyan-500 to-blue-400',
      'from-blue-500 to-indigo-400',
      'from-indigo-500 to-violet-400',
      'from-violet-500 to-purple-400',
      'from-purple-500 to-pink-400',
    ];
    return colors[idx % colors.length];
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full animate-fade-in">
      <div className="mb-10 text-center">
        <div className="flex justify-center mb-4">
          <div className="p-4 bg-gradient-to-br from-primary to-accent rounded-2xl shadow-lg">
            <ChartBarIcon className="h-8 w-8 text-white" />
          </div>
        </div>
        <h1 className="text-3xl md:text-4xl font-heading font-extrabold mb-3">
          Tendances du <span className="text-gradient">Marche</span>
        </h1>
        <p className="text-secondary-foreground text-lg">
          Competences, villes et sources qui dominent les offres de stage.
        </p>
        {data ? (
          <p className="text-sm text-secondary-foreground mt-2">
            Analyse sur <strong>{data.total_offers_analyzed} offres actives</strong>
          </p>
        ) : null}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-24">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : (
        <>
          <div className="glass-card rounded-2xl p-6 md:p-8">
            <div className="flex items-center gap-2 mb-6">
              <FireIcon className="h-5 w-5 text-orange-500" />
              <h2 className="text-lg font-bold font-heading">Top 15 competences</h2>
            </div>

            <div className="flex flex-col gap-4">
              {data?.top_skills.map((item, idx) => (
                <div key={item.skill} className="flex items-center gap-4">
                  <span className={`w-7 text-center text-sm font-bold ${idx < 3 ? 'text-orange-500' : 'text-secondary-foreground'}`}>
                    #{idx + 1}
                  </span>
                  <span className="w-36 text-sm font-medium truncate">{item.skill}</span>
                  <div className="flex-1 bg-secondary rounded-full h-4 overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${getBarColor(idx)} rounded-full transition-all duration-700 ease-out`}
                      style={{ width: `${(item.count / maxCount) * 100}%` }}
                    />
                  </div>
                  <div className="text-right w-24 text-sm">
                    <span className="font-bold">{item.count}</span>
                    <span className="text-secondary-foreground ml-1">({item.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>

            {data?.top_skills.length === 0 ? (
              <p className="text-center text-secondary-foreground py-8">
                Aucune donnee disponible. Lancez le scraper pour remplir la base.
              </p>
            ) : null}
          </div>

          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-lg font-bold font-heading mb-4">Villes les plus actives</h3>
              <div className="space-y-3">
                {data?.top_cities.map((item) => (
                  <div key={item.city} className="flex items-center justify-between text-sm">
                    <span>{item.city}</span>
                    <span className="font-bold">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-lg font-bold font-heading mb-4">Sources les plus utiles</h3>
              <div className="space-y-3">
                {data?.top_platforms.map((item) => (
                  <div key={item.platform} className="flex items-center justify-between text-sm">
                    <span>{item.platform}</span>
                    <span className="font-bold">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
