import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { PriceService } from '../../services/price.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  userName = '';
  alertCount = 0;

  constructor(
    public authService: AuthService,
    private priceService: PriceService,
    private router: Router
  ) {}

  ngOnInit() {
    this.authService.isLoggedIn();
    this.updateUserInfo();
    this.loadAlertCount();
  }

  updateUserInfo() {
    const user = this.authService.getCurrentUser();
    this.userName = user ? user.name : '';
  }

  loadAlertCount() {
    if (this.authService.isLoggedIn()) {
      this.priceService.getAlerts().subscribe(alerts => {
        this.alertCount = alerts.length;
      });
    }
  }

  onLogout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
