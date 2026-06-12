import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PriceService, PaginatedResponse } from '../../services/price.service';
import { Product } from '../../models/price.model';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  products: Product[] = [];
  totalCount: number = 0;
  totalPages: number = 0;
  currentPage: number = 1;
  pageSize: number = 20;
  loading: boolean = false;
  
  searchTerm: string = '';
  selectedSource: string = 'All';
  selectedCategory: string = 'All';
  sortBy: string = 'newest';
  minPrice?: number;
  maxPrice?: number;
  
  isGridView: boolean = true;
  sources: string[] = ['All', 'jumia.ma', 'avito.ma', 'amazon.com', 'connecto.ma'];
  categories: string[] = ['All', 'Informatique', 'Smartphones', 'Tablets', 'TVs', 'Electromenager'];
  
  sourceStats: any[] = [
    { name: 'jumia.ma', count: 0, icon: 'bi-shop', color: 'orange' },
    { name: 'avito.ma', count: 0, icon: 'bi-shop', color: 'blue' },
    { name: 'amazon.com', count: 0, icon: 'bi-shop', color: 'green' },
    { name: 'connecto.ma', count: 0, icon: 'bi-shop', color: 'purple' }
  ];

  Math = Math;

  constructor(private priceService: PriceService) {}

  ngOnInit(): void {
    this.loadProducts();
    this.loadStats();
  }

  loadProducts(): void {
    this.loading = true;
    this.priceService.getPrices(
      this.selectedSource,
      this.selectedCategory,
      this.searchTerm,
      this.currentPage,
      this.pageSize,
      this.sortBy
    ).subscribe({
      next: (res: PaginatedResponse) => {
        this.products = res.products;
        this.totalCount = res.total;
        this.totalPages = res.total_pages;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading products', err);
        this.loading = false;
      }
    });
  }

  loadStats(): void {
    forkJoin({
      jumia: this.priceService.getPrices('jumia.ma', 'All', '', 1, 1),
      avito: this.priceService.getPrices('avito.ma', 'All', '', 1, 1),
      amazon: this.priceService.getPrices('amazon.com', 'All', '', 1, 1),
      connecto: this.priceService.getPrices('connecto.ma', 'All', '', 1, 1)
    }).subscribe(res => {
      this.sourceStats[0].count = res.jumia.total;
      this.sourceStats[1].count = res.avito.total;
      this.sourceStats[2].count = res.amazon.total;
      this.sourceStats[3].count = res.connecto.total;
    });
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadProducts();
  }

  onSearchChange(value: string): void {
    this.searchTerm = value;
    if (!value) {
      this.onFilterChange();
    }
  }

  selectSource(source: string): void {
    this.selectedSource = source;
    this.onFilterChange();
  }

  selectCategory(category: string): void {
    this.selectedCategory = category;
    this.onFilterChange();
  }

  prevPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadProducts();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadProducts();
    }
  }

  onImageError(event: any): void {
    event.target.src = 'assets/images/it.jpg';
  }

  openProductLink(product: Product): void {
    window.open(product.url, '_blank');
  }

  exportCSV(): void {
    this.priceService.getFullData().subscribe(data => {
      const replacer = (key: any, value: any) => value === null ? '' : value;
      const header = Object.keys(data[0]);
      let csv = data.map((row: any) => header.map(fieldName => JSON.stringify(row[fieldName], replacer)).join(','));
      csv.unshift(header.join(','));
      let csvArray = csv.join('\r\n');

      var blob = new Blob([csvArray], {type: 'text/csv' });
      var url = window.URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'market_inventory.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    });
  }
}
