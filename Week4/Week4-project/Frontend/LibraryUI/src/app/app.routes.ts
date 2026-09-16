import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login';
import { BookListComponent } from './book-list/book-list';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [

  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'books',
    component: BookListComponent,
    canActivate: [authGuard]
  },

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  }
];