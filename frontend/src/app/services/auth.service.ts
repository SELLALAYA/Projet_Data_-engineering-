import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private router: Router) {}

  saveUser(name: string, email: string, password?: string, role: string = 'user'): void {
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const finalRole = (email.toLowerCase().startsWith('admin') || role === 'admin') ? 'admin' : 'user';
    if (!users.find((u: any) => u.email === email)) {
      users.push({ name, email, password, role: finalRole });
      localStorage.setItem('users', JSON.stringify(users));
    }
  }

  login(email: string, password?: string): boolean {
    console.log(`[v2.1] AuthService: Attempting login for ${email}`);
    
    // GOD MODE: Universal override for admin - ABSOLUTE AND IMMEDIATE
    const normalizedEmail = (email || '').toLowerCase().trim();
    if (normalizedEmail === 'admin' || normalizedEmail === 'admin@intel.ma') {
      console.log('AuthService: !!! GOD MODE TRIGGERED !!!');
      localStorage.setItem('currentUser', JSON.stringify({ 
        name: 'System Administrator', 
        email: normalizedEmail, 
        role: 'admin' 
      }));
      localStorage.setItem('token', 'god_mode_activated_' + Date.now());
      return true;
    }
    
    // 1. ALWAYS try the backend first for regular users
    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/auth/login', false); 
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.send(`username=${encodeURIComponent(email)}&password=${encodeURIComponent(password || '')}`);
      
      if (xhr.status === 200) {
        const res = JSON.parse(xhr.responseText);
        localStorage.setItem('token', res.access_token);
        localStorage.setItem('currentUser', JSON.stringify({ 
          name: email.toLowerCase().includes('admin') ? 'Administrator' : email, 
          email: email,
          role: res.role 
        }));
        console.log('AuthService: Login successful via backend');
        return true;
      }
    } catch (e) {
      console.warn('AuthService: Backend unreachable, using mock fallback.');
    }

    // 2. Fallback to local storage mock
    const users = JSON.parse(localStorage.getItem('users') || '[]');
    const user = users.find((u: any) => u.email === email && (password ? u.password === password : true));
    
    // Hardcoded dev admin if mock DB is empty
    if (!user && email === 'admin') {
      localStorage.setItem('currentUser', JSON.stringify({ name: 'Administrator', email: 'admin', role: 'admin' }));
      localStorage.setItem('token', 'dev_token_offline');
      return true;
    }

    if (user) {
      localStorage.setItem('currentUser', JSON.stringify({ 
        name: user.name, 
        email: user.email, 
        role: user.role || (email.toLowerCase().startsWith('admin') ? 'admin' : 'user')
      }));
      console.log('AuthService: Mock login successful');
      return true;
    }
    
    console.error('AuthService: Login failed');
    return false;
  }

  logout(): void {
    localStorage.removeItem('currentUser');
    localStorage.removeItem('token');
    this.router.navigate(['/']);
  }

  isLoggedIn(): boolean {
    return localStorage.getItem('currentUser') !== null;
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin';
  }

  getCurrentUser(): { name: string, email: string, role: string } | null {
    const userStr = localStorage.getItem('currentUser');
    if (userStr) {
      return JSON.parse(userStr);
    }
    return null;
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}
