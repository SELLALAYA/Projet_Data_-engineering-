import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PriceService } from '../../services/price.service';
import { Product } from '../../models/price.model';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent implements OnInit {
  topAlerts: Product[] = [];
  loading: boolean = true;

  constructor(private priceService: PriceService) {}

  ngOnInit(): void {
    this.loadTopAlerts();
  }

  loadTopAlerts(): void {
    this.loading = true;
    this.priceService.getAlerts().subscribe({
      next: (res) => {
        // Take the top 3 biggest discounts for the hero showcase
        this.topAlerts = res.slice(0, 3);
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading top alerts for landing', err);
        this.loading = false;
      }
    });
  }

  openProductLink(product: Product): void {
    window.open(product.url, '_blank');
  }
}
