import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { Product } from '../models/price.model';

export interface PaginatedResponse {
  total: number;
  products: Product[];
  page: number;
  limit: number;
  total_pages: number;
}

@Injectable({
  providedIn: 'root'
})
export class PriceService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`).pipe(
      tap(h => console.log('[PriceService] Health Check:', h)),
      catchError(err => {
        console.error('[PriceService] Health Check FAILED:', err);
        return of({status: 'error'});
      })
    );
  }

  getPrices(
    source?: string,
    category?: string,
    search?: string,
    page: number = 1,
    limit: number = 50,
    sortBy: string = 'newest'
  ): Observable<PaginatedResponse> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString())
      .set('sort_by', sortBy);
    if (source && source !== 'All') params = params.set('source', source);
    if (category && category !== 'All') params = params.set('category', category);
    if (search && search.trim() !== '') params = params.set('search', search.trim());
    const fullUrl = `${this.apiUrl}/prices`;
    console.log(`[PriceService] Fetching products: ${fullUrl}`, params.toString());
    return this.http.get<any>(fullUrl, { params }).pipe(
      tap(res => {
        if (res && res.error) {
          console.error('[PriceService] API returned error:', res.error);
          throw new Error(res.error);
        }
        console.log('[PriceService] Products loaded:', res);
      }),
      catchError(err => {
        console.error('[PriceService] API Error:', err);
        throw err;
      })
    );
  }

  getStats(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/prices/stats`).pipe(
      tap((res: any) => {
        if (res && res.error) throw new Error(res.error);
      })
    );
  }

  getTopDiscounts(): Observable<Product[]> {
    return this.http.get<any>(`${this.apiUrl}/prices/top-discounts`).pipe(
      tap((res: any) => {
        if (res && res.error) throw new Error(res.error);
      })
    );
  }

  getByCategory(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/prices/by-category`).pipe(
      tap((res: any) => {
        if (res && res.error) throw new Error(res.error);
      })
    );
  }

  getAlerts(): Observable<Product[]> {
    return this.http.get<any>(`${this.apiUrl}/prices/alerts`).pipe(
      tap((res: any) => {
        if (res && res.error) throw new Error(res.error);
      })
    );
  }

  getStatistics(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/statistics`);
  }

  getDescriptive(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/descriptive`);
  }

  getRegression(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/regression`);
  }

  getMannWhitney(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/mannwhitney`);
  }

  getAnovaCategory(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/anova-category`);
  }

  getPower(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/power`);
  }

  getTrends(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/prices/trends`);
  }

  getVelocity(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/prices/velocity`);
  }

  getFullData(): Observable<any> {
    return this.http.get(`${this.apiUrl}/prices/full-data`);
  }

  triggerPipeline(): Observable<any> {
    return this.http.post(`${this.apiUrl}/pipeline/trigger`, {});
  }
}