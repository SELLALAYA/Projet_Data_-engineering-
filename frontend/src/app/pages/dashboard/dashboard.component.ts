import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import {
  Chart,
  ChartConfiguration,
  ChartData,
  ChartType,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
  DoughnutController,
  BarController
} from 'chart.js';
import { PriceService } from '../../services/price.service';
import { AuthService } from '../../services/auth.service';
import { Product } from '../../models/price.model';

// ✅ Required: Register all Chart.js components used
Chart.register(
  BarElement, ArcElement,
  CategoryScale, LinearScale,
  Legend, Tooltip,
  DoughnutController, BarController
);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, BaseChartDirective],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  userName: string = 'User';
  totalProducts: number = 0;
  alertCount: number = 0;
  avgPrice: number = 0;
  bestDeal: Product | null = null;
  currentDay: string = '';
  currentDate: string = '';
  
  stats: any[] = [];
  topDiscounts: Product[] = [];

  // Bar Chart
  public barChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true }
    }
  };
  public barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [
      { data: [], label: 'Avg Price (MAD)', backgroundColor: '#f97316' }
    ]
  };

  // Doughnut Chart
  public doughnutChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' }
    }
  };
  public doughnutChartData: ChartData<'doughnut'> = {
    labels: [],
    datasets: [
      { data: [], backgroundColor: ['#f68b1e', '#ff0000', '#000000', '#003399'] }
    ]
  };

  constructor(
    private priceService: PriceService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const user = this.authService.getCurrentUser();
    if (user) this.userName = user.name;
    
    this.updateDateTime();
    this.loadDashboardData();
  }

  updateDateTime(): void {
    const now = new Date();
    this.currentDay = now.toLocaleDateString('en-US', { weekday: 'long' });
    this.currentDate = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }

  loadDashboardData(): void {
    // Basic Stats
    this.priceService.getStats().subscribe(res => {
      this.totalProducts = res.total_products;
      this.avgPrice = res.avg_price;
    });

    // Top Discounts
    this.priceService.getTopDiscounts().subscribe(res => {
      this.topDiscounts = res;
      if (res.length > 0) this.bestDeal = res[0];
    });

    // Alerts
    this.priceService.getAlerts().subscribe(res => {
      this.alertCount = res.length;
    });

    // Detailed Stats for Charts
    this.priceService.getDescriptive().subscribe(res => {
      this.stats = this.processSourceStats(res);
      this.updateCharts(this.stats);
    });
  }

  processSourceStats(data: any[]): any[] {
    if (!data || !Array.isArray(data)) return [];
    const sources = [...new Set(data.map(item => item.source))];
    return sources.map(s => {
      const sourceItems = data.filter(item => item.source === s);
      const totalProducts = sourceItems.reduce((acc, curr) => acc + curr.count, 0);
      const avgPrice = sourceItems.reduce((acc, curr) => acc + (curr.mean * curr.count), 0) / totalProducts;
      return {
        source: s,
        total_products: totalProducts,
        avg_price: avgPrice
      };
    });
  }

  updateCharts(stats: any[]): void {
    if (!stats || stats.length === 0) return;

    // ✅ Spread-assign new objects — mutation does NOT trigger ng2-charts change detection
    this.barChartData = {
      labels: stats.map(s => s.source),
      datasets: [{
        ...this.barChartData.datasets[0],
        data: stats.map(s => Math.round(s.avg_price))
      }]
    };

    this.doughnutChartData = {
      labels: stats.map(s => s.source),
      datasets: [{
        ...this.doughnutChartData.datasets[0],
        data: stats.map(s => s.total_products)
      }]
    };
  }

  navigateToSource(source: string): void {
    this.router.navigate(['/products'], { queryParams: { source: source } });
  }

  openProductLink(product: Product): void {
    window.open(product.url, '_blank');
  }
}
