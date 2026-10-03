import {
  Component
} from '@angular/core';

import {
  Router,
  RouterOutlet,
  RouterLink
} from '@angular/router';

import {
  AuthService
} from './services/auth';

@Component({
  selector: 'app-root',
  standalone: true,

  imports: [
    RouterOutlet,
    RouterLink
  ],

  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  logout(): void {

    this.authService.logout();

    this.router.navigate([
      '/login'
    ]);
  }
}