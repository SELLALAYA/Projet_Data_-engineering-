import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  name = '';
  email = '';
  password = '';
  error = '';
  loading = false;

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    this.loading = true;
    this.error = '';

    setTimeout(() => {
      this.authService.saveUser(this.name, this.email, this.password);
      const success = this.authService.login(this.email, this.password);
      if (success) {
        this.router.navigate(['/dashboard']);
      } else {
        this.error = 'System Error: Profile creation failed.';
      }
      this.loading = false;
    }, 800);
  }
}
