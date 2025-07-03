import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  Bot,
  Campaign,
  TrendingUp,
  Users,
  Plus,
  ExternalLink,
} from 'lucide-react';

const Dashboard = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const response = await dashboardAPI.getOverview();
        setOverview(response.data);
      } catch (err) {
        setError('Erro ao carregar dados do dashboard');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Tentar novamente
        </Button>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total de Campanhas',
      value: overview?.overview?.total_campaigns || 0,
      icon: Campaign,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Campanhas Ativas',
      value: overview?.overview?.active_campaigns || 0,
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Bots do Telegram',
      value: overview?.overview?.total_bots || 0,
      icon: Bot,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Total de Leads',
      value: overview?.overview?.total_leads || 0,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Visão geral das suas campanhas de rastreamento UTM
          </p>
        </div>
        <div className="flex space-x-3">
          <Button asChild>
            <Link to="/campaigns/new">
              <Plus className="h-4 w-4 mr-2" />
              Nova Campanha
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Campaigns */}
        <Card>
          <CardHeader>
            <CardTitle>Campanhas com Mais Leads</CardTitle>
            <CardDescription>
              Suas campanhas mais performáticas
            </CardDescription>
          </CardHeader>
          <CardContent>
            {overview?.top_campaigns?.length > 0 ? (
              <div className="space-y-4">
                {overview.top_campaigns.slice(0, 5).map((campaign, index) => (
                  <div key={campaign.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600">
                            {index + 1}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {campaign.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {campaign.lead_count} leads
                        </p>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/campaigns/${campaign.id}`}>
                        <ExternalLink className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Campaign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Nenhuma campanha encontrada</p>
                <Button asChild className="mt-4">
                  <Link to="/campaigns/new">Criar primeira campanha</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Atividade Recente</CardTitle>
            <CardDescription>
              Últimos leads capturados
            </CardDescription>
          </CardHeader>
          <CardContent>
            {overview?.recent_activity?.length > 0 ? (
              <div className="space-y-4">
                {overview.recent_activity.slice(0, 5).map((lead) => (
                  <div key={lead.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                          <Users className="h-4 w-4 text-green-600" />
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {lead.first_name || lead.username || 'Usuário'}
                        </p>
                        <div className="flex items-center space-x-2">
                          {lead.utm_source && (
                            <Badge variant="secondary" className="text-xs">
                              {lead.utm_source}
                            </Badge>
                          )}
                          {lead.utm_campaign && (
                            <Badge variant="outline" className="text-xs">
                              {lead.utm_campaign}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">
                        {lead.campaign_name}
                      </p>
                      <p className="text-xs text-gray-400">
                        {new Date(lead.created_at).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Nenhuma atividade recente</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* UTM Sources */}
      {overview?.utm_sources?.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Principais Fontes UTM</CardTitle>
            <CardDescription>
              De onde vêm seus leads
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {overview.utm_sources.slice(0, 5).map((source, index) => (
                <div key={index} className="text-center">
                  <div className="bg-gray-100 rounded-lg p-4">
                    <BarChart3 className="h-8 w-8 text-gray-600 mx-auto mb-2" />
                    <p className="text-lg font-bold text-gray-900">
                      {source.count}
                    </p>
                    <p className="text-sm text-gray-600">
                      {source.source}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <CardDescription>
            Comece a usar o UTM Tracker
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button asChild variant="outline" className="h-auto p-4">
              <Link to="/telegram-bots/new" className="flex flex-col items-center space-y-2">
                <Bot className="h-8 w-8" />
                <span>Adicionar Bot</span>
                <span className="text-xs text-gray-500">
                  Configure um bot do Telegram
                </span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4">
              <Link to="/campaigns/new" className="flex flex-col items-center space-y-2">
                <Campaign className="h-8 w-8" />
                <span>Nova Campanha</span>
                <span className="text-xs text-gray-500">
                  Crie uma campanha de rastreamento
                </span>
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-auto p-4">
              <Link to="/analytics" className="flex flex-col items-center space-y-2">
                <BarChart3 className="h-8 w-8" />
                <span>Ver Analytics</span>
                <span className="text-xs text-gray-500">
                  Analise seus dados
                </span>
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

