import {
  Routes
} from '@angular/router';

import {
  LoginComponent
} from './components/login/login';

import {
  BookListComponent
} from './book-list/book-list';

import {
  ChatComponent
} from './components/chat/chat';

import {
  authGuard
} from './guards/auth-guard';

import {
  AgentRunComponent
} from './agent-run/agent-run.component';

export const routes:
  Routes = [

  {
    path: 'login',
    component: LoginComponent
  },

  {
    path: 'books',
    component: BookListComponent,
    canActivate: [
      authGuard
    ]
  },

  {
  path: 'agent',
  component: AgentRunComponent
},
  {
    path: 'chat',
    component: ChatComponent,
    canActivate: [
      authGuard
    ]
  },

  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full'
  }

];