import { Routes } from '@angular/router';
import { LandingComponent } from './pages/landing/landing.component';
import { LoginComponent } from './pages/login/login.component';
import { RegisterComponent } from './pages/register/register.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ProductsComponent } from './pages/products/products.component';
import { AlertsComponent } from './pages/alerts/alerts.component';
import { AnalysisComponent } from './pages/analysis/analysis.component';
import { AuthGuard } from './guards/auth.guard';
import { RoleGuard } from './guards/role.guard';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'products', component: ProductsComponent, canActivate: [AuthGuard] },
  { path: 'alerts', component: AlertsComponent, canActivate: [AuthGuard] },
  { path: 'analysis', component: AnalysisComponent, canActivate: [AuthGuard, RoleGuard] },
  { path: '**', redirectTo: '' }
];