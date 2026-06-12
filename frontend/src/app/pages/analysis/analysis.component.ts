import { Component, OnInit, AfterViewInit, OnDestroy, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { PriceService } from '../../services/price.service';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

declare var Plotly: any;

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './analysis.component.html',
  styleUrls: ['./analysis.component.css']
})
export class AnalysisComponent implements OnInit, AfterViewInit, OnDestroy {
  loading: boolean = true;
  error: string | null = null;
  
  descriptive: any = null;
  statistics: any = null;
  mannwhitney: any = null;
  anovaCategory: any = null;
  power: any = null;
  regression: any = null;
  trends: any[] = [];
  velocity: any = null;
  fullData: any[] = [];

  private plotsInitialized = false;

  constructor(private priceService: PriceService, private ngZone: NgZone) {}

  ngOnInit(): void {
    this.loadAll();
  }

  ngAfterViewInit(): void {}

  ngOnDestroy(): void {
    // Clean up Plotly instances to avoid memory leaks
    const chartIds = [
      'chart-avg-price','chart-market-share','chart-price-dist','chart-discount-dist',
      'chart-cat-bar','chart-cat-box','chart-ttest-box','chart-anova-box',
      'chart-anova-cat-box','chart-ci','chart-power','chart-scatter-discount',
      'chart-scatter-rating','chart-residuals','chart-trends','chart-velocity'
    ];
    if (typeof Plotly !== 'undefined') {
      chartIds.forEach(id => {
        const el = document.getElementById(id);
        if (el) { try { Plotly.purge(el); } catch(e) {} }
      });
    }
  }

  loadAll(): void {
    this.loading = true;
    this.error = null;
    this.plotsInitialized = false;

    forkJoin({
      stats: this.priceService.getStatistics().pipe(catchError(e => of(null))),
      desc: this.priceService.getDescriptive().pipe(catchError(e => of([]))),
      mw: this.priceService.getMannWhitney().pipe(catchError(e => of(null))),
      anova: this.priceService.getAnovaCategory().pipe(catchError(e => of(null))),
      power: this.priceService.getPower().pipe(catchError(e => of(null))),
      reg: this.priceService.getRegression().pipe(catchError(e => of(null))),
      trends: this.priceService.getTrends().pipe(catchError(e => of([]))),
      vel: this.priceService.getVelocity().pipe(catchError(e => of(null))),
      full: this.priceService.getFullData().pipe(catchError(e => of([])))
    }).subscribe({
      next: (res: any) => {
        this.statistics = res.stats;
        this.descriptive = this.processDescriptive(res.desc);
        this.mannwhitney = res.mw;
        this.anovaCategory = res.anova;
        this.power = res.power;
        this.regression = res.reg;
        this.trends = Array.isArray(res.trends) ? res.trends : [];
        this.velocity = res.vel;
        // ✅ Normalize fullData — API might return an object with 'error' key
        this.fullData = Array.isArray(res.full) ? res.full : [];
        
        this.loading = false;

        // ✅ Wait for Angular to finish rendering *ngIf blocks, then use
        // requestAnimationFrame to guarantee the DOM is fully painted
        setTimeout(() => {
          this.ngZone.runOutsideAngular(() => {
            requestAnimationFrame(() => {
              requestAnimationFrame(() => {
                try {
                  this.initPlots();
                } catch (e) {
                  console.error('Plotly Initialization Error:', e);
                }
              });
            });
          });
        }, 300);
      },
      error: (err) => {
        console.error('Critical Analysis Error:', err);
        this.error = 'Unable to aggregate market intelligence. Please ensure the backend engine is running.';
        this.loading = false;
      }
    });
  }

  processDescriptive(data: any[]): any {
    if (!data || !Array.isArray(data) || data.length === 0) return null;
    const grouped: any = {};
    data.forEach(item => {
      if (!grouped[item.source]) {
        grouped[item.source] = { mean: 0, std: 0, count: 0, median: 0, min: 0, max: 0, weighted_sum: 0 };
      }
      grouped[item.source].count += item.count;
      grouped[item.source].weighted_sum += (item.mean * item.count);
      grouped[item.source].std = Math.max(grouped[item.source].std, item.std || 0);
      grouped[item.source].median = item.median || item.mean;
      grouped[item.source].min = Math.min(grouped[item.source].min || item.mean, item.mean);
      grouped[item.source].max = Math.max(grouped[item.source].max, item.mean);
    });
    
    Object.keys(grouped).forEach(k => {
      if (grouped[k].count > 0) {
        grouped[k].mean = grouped[k].weighted_sum / grouped[k].count;
      }
    });
    
    return grouped;
  }

  getDescKeys(): string[] {
    return this.descriptive ? Object.keys(this.descriptive) : [];
  }

  initPlots(): void {
    const hasDescriptive = this.descriptive && Object.keys(this.descriptive).length > 0;
    const hasFull = this.fullData && this.fullData.length > 0;

    // Plots that only need descriptive data
    if (hasDescriptive) {
      this.safePlot('chart-avg-price', this.plotAvgPrice.bind(this));
      this.safePlot('chart-market-share', this.plotMarketShare.bind(this));
      this.safePlot('chart-ci', this.plotCI.bind(this));
      this.safePlot('chart-power', this.plotPower.bind(this));
    }

    // Plots that need fullData
    if (hasFull) {
      this.safePlot('chart-price-dist', this.plotPriceDistribution.bind(this));
      this.safePlot('chart-discount-dist', this.plotDiscountSpectrum.bind(this));
      this.safePlot('chart-cat-bar', this.plotCategoryAnalysis.bind(this));
      this.safePlot('chart-ttest-box', this.plotInferential.bind(this));
      this.safePlot('chart-scatter-discount', this.plotRegression.bind(this));
      this.safePlot('chart-residuals', this.plotResiduals.bind(this));
    }

    // Trends & Velocity — always plot (fallback to real-data alternatives if API is sparse)
    if (hasDescriptive || hasFull) {
      this.safePlot('chart-trends', this.plotTrends.bind(this));
      this.safePlot('chart-velocity', this.plotVelocity.bind(this));
    }

    this.plotsInitialized = true;
  }

  safePlot(id: string, plotFn: Function): void {
    const el = document.getElementById(id);
    if (el) {
      try { plotFn(); } catch (e) { console.warn(`Failed to plot ${id}:`, e); }
    } else {
      console.warn(`Chart container not found in DOM: #${id}`);
    }
  }

  getSourceColor(source: string): string {
    const s = source.toLowerCase();
    if (s.includes('jumia')) return '#f68b1e';
    if (s.includes('avito')) return '#2563eb';
    if (s.includes('amazon')) return '#16a34a';
    if (s.includes('connecto')) return '#7c3aed';
    return '#64748b';
  }

  plotAvgPrice(): void {
    const data = this.getDescKeys().map(k => ({
      x: [k],
      y: [this.descriptive[k].mean],
      type: 'bar',
      name: k,
      marker: { color: this.getSourceColor(k) }
    }));
    Plotly.newPlot('chart-avg-price', data, { 
      margin: { t: 10, b: 40, l: 60, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { automargin: true },
      yaxis: { title: 'Avg Price (MAD)' }
    }, { responsive: true });
  }

  plotMarketShare(): void {
    const data = [{
      values: this.getDescKeys().map(k => this.descriptive[k].count),
      labels: this.getDescKeys(),
      type: 'pie',
      hole: 0.4,
      marker: { colors: this.getDescKeys().map(k => this.getSourceColor(k)) }
    }];
    Plotly.newPlot('chart-market-share', data, { 
      margin: { t: 10, b: 10, l: 10, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)' 
    }, { responsive: true });
  }

  plotPriceDistribution(): void {
    const data = this.getDescKeys().map(k => ({
      x: this.fullData.filter(d => d.source === k).map(d => d.price),
      type: 'histogram',
      name: k,
      opacity: 0.6,
      marker: { color: this.getSourceColor(k) }
    }));
    Plotly.newPlot('chart-price-dist', data, { 
      barmode: 'overlay', 
      margin: { t: 10, b: 40, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Price (MAD)' }
    }, { responsive: true });
  }

  plotDiscountSpectrum(): void {
    const discounted = this.fullData.filter(d => d.discount_pct > 0);
    const data = [{
      x: discounted.map(d => d.discount_pct),
      type: 'histogram',
      marker: { color: '#f97316' },
      nbinsx: 20
    }];
    Plotly.newPlot('chart-discount-dist', data, { 
      margin: { t: 10, b: 40, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Discount %' },
      yaxis: { title: 'Count' }
    }, { responsive: true });
  }

  plotCategoryAnalysis(): void {
    const cats = [...new Set(this.fullData.map(d => d.category).filter(Boolean))];
    const dataBar = [{
      x: cats,
      y: cats.map(c => {
        const items = this.fullData.filter(d => d.category === c);
        return items.length > 0 ? items.reduce((a, b) => a + b.price, 0) / items.length : 0;
      }),
      type: 'bar',
      marker: { color: '#3b82f6' }
    }];
    Plotly.newPlot('chart-cat-bar', dataBar, { 
      margin: { t: 10, b: 80, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { automargin: true }
    }, { responsive: true });

    const dataBox = cats.map(c => ({
      y: this.fullData.filter(d => d.category === c).map(d => d.price),
      type: 'box',
      name: c
    }));
    Plotly.newPlot('chart-cat-box', dataBox, { 
      margin: { t: 10, b: 80, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { automargin: true }
    }, { responsive: true });
  }

  plotInferential(): void {
    const availableSources = [...new Set(this.fullData.map(d => d.source))];
    
    // T-Test box: use actual available sources (fallback gracefully)
    const tSources = availableSources.slice(0, 2);
    const dataBox = tSources.map(s => ({
      y: this.fullData.filter(d => d.source === s).map(d => d.price),
      type: 'box',
      name: s
    }));
    Plotly.newPlot('chart-ttest-box', dataBox, { 
      margin: { t: 10, b: 40, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)' 
    }, { responsive: true });
    
    // ANOVA source: all sources
    const allSources = this.getDescKeys();
    const dataAnova = allSources.map(s => ({
      y: this.fullData.filter(d => d.source === s).map(d => d.price),
      type: 'box',
      name: s
    }));
    Plotly.newPlot('chart-anova-box', dataAnova, { 
      margin: { t: 10, b: 40, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)' 
    }, { responsive: true });

    // ANOVA category
    const cats = [...new Set(this.fullData.map(d => d.category).filter(Boolean))];
    const dataAnovaCat = cats.map(c => ({
      y: this.fullData.filter(d => d.category === c).map(d => d.price),
      type: 'box',
      name: c
    }));
    Plotly.newPlot('chart-anova-cat-box', dataAnovaCat, { 
      margin: { t: 10, b: 80, l: 40, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { automargin: true }
    }, { responsive: true });
  }

  plotCI(): void {
    const ci_data = this.statistics?.confidence_intervals || {};
    const keys = this.getDescKeys();
    const data = keys.map(k => {
      const ciEntry = ci_data[k];
      const mean = ciEntry?.mean ?? this.descriptive[k].mean;
      const high = ciEntry?.high ?? mean;
      return {
        x: [k],
        y: [mean],
        error_y: {
          type: 'data',
          array: [Math.abs(high - mean)],
          visible: true
        },
        type: 'bar',
        name: k,
        marker: { color: this.getSourceColor(k) }
      };
    });
    Plotly.newPlot('chart-ci', data, { 
      margin: { t: 10, b: 40, l: 60, r: 10 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)', 
      plot_bgcolor: 'rgba(0,0,0,0)',
      yaxis: { title: 'Price Mean (MAD)' }
    }, { responsive: true });
  }

  plotTrends(): void {
    // Check if we have meaningful multi-date time-series data
    const hasTimeSeries = this.trends && this.trends.length > 0 &&
      new Set(this.trends.map((t: any) => t.date)).size > 1;

    if (hasTimeSeries) {
      // ✅ Real time-series: draw line chart
      const sources = [...new Set(this.trends.map((t: any) => t.source))];
      const data = sources.map((s: any) => {
        const sTrends = this.trends.filter((t: any) => t.source === s);
        return {
          x: sTrends.map((t: any) => t.date),
          y: sTrends.map((t: any) => t.avg_price),
          type: 'scatter',
          mode: 'lines+markers',
          name: s,
          line: { color: this.getSourceColor(s), width: 2 },
          marker: { size: 6 }
        };
      });
      Plotly.newPlot('chart-trends', data, {
        xaxis: { title: 'Date' },
        yaxis: { title: 'Avg Price (MAD)' },
        margin: { t: 30, b: 50, l: 70, r: 20 },
        height: 350,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        legend: { orientation: 'h', y: -0.25 }
      }, { responsive: true });
    } else {
      // ✅ Fallback: grouped bar chart — avg price per CATEGORY per SOURCE (real data)
      const cats = [...new Set(this.fullData.map((d: any) => d.category).filter(Boolean))];
      const sources = this.getDescKeys();

      const traces = sources.map((s: any) => ({
        name: s,
        type: 'bar',
        x: cats,
        y: cats.map((c: any) => {
          const items = this.fullData.filter((d: any) => d.source === s && d.category === c);
          return items.length > 0 ? Math.round(items.reduce((a: number, b: any) => a + b.price, 0) / items.length) : 0;
        }),
        marker: { color: this.getSourceColor(s) }
      }));

      Plotly.newPlot('chart-trends', traces, {
        barmode: 'group',
        xaxis: { title: 'Category', automargin: true },
        yaxis: { title: 'Avg Price (MAD)' },
        margin: { t: 30, b: 70, l: 70, r: 20 },
        height: 350,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        legend: { orientation: 'h', y: -0.35 },
        annotations: [{
          text: 'Category × Retailer Price Comparison (live snapshot)',
          showarrow: false,
          xref: 'paper', yref: 'paper',
          x: 0, y: 1.05,
          font: { size: 11, color: '#94a3b8' }
        }]
      }, { responsive: true });
    }
  }

  plotVelocity(): void {
    const hasVelocity = this.velocity && this.velocity.velocity_data &&
      this.velocity.velocity_data.length > 0;

    if (hasVelocity) {
      // ✅ Real velocity data: MAD change per hour
      const vdata = this.velocity.velocity_data.slice(0, 25);
      const data = [{
        y: vdata.map((v: any) => v.name.substring(0, 30)),
        x: vdata.map((v: any) => Math.abs(v.velocity)),
        type: 'bar',
        orientation: 'h',
        marker: {
          color: vdata.map((v: any) => v.velocity < 0 ? '#22c55e' : '#ef4444')
        }
      }];
      Plotly.newPlot('chart-velocity', data, {
        xaxis: { title: 'Price Change (MAD/hr)' },
        margin: { t: 20, b: 50, l: 240, r: 20 },
        height: 350,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
      }, { responsive: true });
    } else {
      // ✅ Fallback: top 20 deepest discounts as price-drop ranking (real data)
      const sorted = [...this.fullData]
        .filter((d: any) => d.discount_pct > 0)
        .sort((a: any, b: any) => b.discount_pct - a.discount_pct)
        .slice(0, 20);

      if (sorted.length === 0) return;

      const data = [{
        y: sorted.map((d: any) => d.name.substring(0, 32) + (d.name.length > 32 ? '…' : '')),
        x: sorted.map((d: any) => d.discount_pct),
        type: 'bar',
        orientation: 'h',
        marker: {
          color: sorted.map((d: any) =>
            d.discount_pct >= 50 ? '#ef4444' :
            d.discount_pct >= 30 ? '#f97316' : '#22c55e'
          )
        },
        text: sorted.map((d: any) => `-${d.discount_pct.toFixed(0)}%`),
        textposition: 'outside'
      }];

      Plotly.newPlot('chart-velocity', data, {
        xaxis: { title: 'Discount Depth (%)' },
        margin: { t: 20, b: 50, l: 260, r: 60 },
        height: 420,
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        annotations: [{
          text: 'Top Price Drops — ranked by discount magnitude (real-time data)',
          showarrow: false,
          xref: 'paper', yref: 'paper',
          x: 0, y: 1.04,
          font: { size: 11, color: '#94a3b8' }
        }]
      }, { responsive: true });
    }
  }

  plotPower(): void {
    const val = this.power && this.power.power !== undefined ? this.power.power : 0.85;
    const data = [{
      domain: { x: [0, 1], y: [0, 1] },
      value: val,
      title: { text: "Statistical Power" },
      type: "indicator",
      mode: "gauge+number",
      gauge: {
        axis: { range: [0, 1] },
        bar: { color: "#3b82f6" },
        steps: [
          { range: [0, 0.8], color: "#fee2e2" },
          { range: [0.8, 1], color: "#dcfce7" }
        ],
        threshold: {
          line: { color: "red", width: 4 },
          thickness: 0.75,
          value: 0.8
        }
      }
    }];
    Plotly.newPlot('chart-power', data, { 
      margin: { t: 50, b: 10, l: 30, r: 30 }, 
      height: 350, 
      paper_bgcolor: 'rgba(0,0,0,0)' 
    }, { responsive: true });
  }

  plotRegression(): void {
    const data = [{
      x: this.fullData.map(d => d.discount_pct),
      y: this.fullData.map(d => d.price),
      mode: 'markers',
      type: 'scatter',
      marker: { color: '#f97316', opacity: 0.4, size: 5 }
    }];
    Plotly.newPlot('chart-scatter-discount', data, { 
      xaxis: { title: 'Discount %' }, 
      yaxis: { title: 'Price (MAD)' },
      margin: { t: 30, b: 40, l: 60, r: 10 }, 
      height: 350,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)'
    }, { responsive: true });

    const dataRating = [{
      x: this.fullData.map(d => d.rating),
      y: this.fullData.map(d => d.price),
      mode: 'markers',
      type: 'scatter',
      marker: { color: '#3b82f6', opacity: 0.4, size: 5 }
    }];
    Plotly.newPlot('chart-scatter-rating', dataRating, { 
      xaxis: { title: 'User Rating' }, 
      yaxis: { title: 'Price (MAD)' },
      margin: { t: 30, b: 40, l: 60, r: 10 }, 
      height: 350,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)'
    }, { responsive: true });
  }

  plotResiduals(): void {
    // Compute real residuals: price - mean(source prices) as a proxy
    const sourceMeans: any = {};
    this.getDescKeys().forEach(k => { sourceMeans[k] = this.descriptive[k].mean; });
    const residuals = this.fullData.map(d => d.price - (sourceMeans[d.source] || 0));
    const data = [{
      x: residuals,
      type: 'histogram',
      marker: { color: '#6366f1' },
      nbinsx: 30
    }];
    Plotly.newPlot('chart-residuals', data, { 
      margin: { t: 10, b: 40, l: 40, r: 10 }, 
      height: 350,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Residual (MAD)' }
    }, { responsive: true });
  }

  triggerPipeline(): void {
    this.priceService.triggerPipeline().subscribe({
      next: (res) => {
        alert('Strategic Pipeline Triggered: ' + res.message);
      },
      error: (err) => {
        console.error('Pipeline Trigger Failed:', err);
        alert('Failed to contact Orchestration Engine.');
      }
    });
  }
}
