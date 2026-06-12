import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): boolean {
    if (this.authService.isLoggedIn() && this.authService.isAdmin()) {
      return true;
    } else {
      // Normal user tries to access /analysis, redirect to /dashboard
      alert('Access restricted to administrators');
      this.router.navigate(['/dashboard']);
      return false;
    }
  }
}
