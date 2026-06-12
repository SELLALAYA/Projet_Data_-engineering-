import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PriceService } from '../../services/price.service';
import { Product } from '../../models/price.model';

@Component({
  selector: 'app-alerts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.css']
})
export class AlertsComponent implements OnInit {
  alerts: Product[] = [];
  filteredAlerts: Product[] = [];
  loading: boolean = true;
  error: string | null = null;
  
  sources: string[] = ['All', 'jumia.ma', 'avito.ma', 'amazon.com', 'connecto.ma'];
  selectedSource: string = 'All';
  sortBy: string = 'highest';

  constructor(private priceService: PriceService) {}

  ngOnInit(): void {
    this.loadAlerts();
  }

  loadAlerts(): void {
    this.loading = true;
    this.error = null;
    this.priceService.getAlerts().subscribe({
      next: (res) => {
        this.alerts = res;
        this.onFilterChange();
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading alerts', err);
        this.error = 'Unable to synchronize with the market data stream. Please try again.';
        this.loading = false;
      }
    });
  }

  onFilterChange(): void {
    let filtered = [...this.alerts];
    
    if (this.selectedSource !== 'All') {
      filtered = filtered.filter(a => a.source === this.selectedSource);
    }
    
    if (this.sortBy === 'highest') {
      filtered.sort((a, b) => b.discount_pct - a.discount_pct);
    } else {
      filtered.sort((a, b) => new Date(b.scraped_at).getTime() - new Date(a.scraped_at).getTime());
    }
    
    this.filteredAlerts = filtered;
  }

  openProductLink(alert: Product): void {
    window.open(alert.url, '_blank');
  }
}
