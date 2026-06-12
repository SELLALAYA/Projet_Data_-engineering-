import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    this.loading = true;
    this.error = '';
    
    const cleanEmail = this.email ? this.email.trim() : '';
    console.log('LoginComponent: Submitting with', cleanEmail);
    const success = this.authService.login(cleanEmail, this.password);
    
    if (success) {
      console.log('LoginComponent: Success! Navigating to dashboard');
      this.router.navigate(['/dashboard']);
    } else {
      console.error('LoginComponent: AuthService returned false');
      this.error = 'Access Denied: Invalid corporate credentials.';
    }
    this.loading = false;
  }
}
