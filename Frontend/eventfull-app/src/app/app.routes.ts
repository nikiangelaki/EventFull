import { Routes } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { EventSearchComponent } from './components/event-search/event-search';
import { EventDetailsComponent } from './components/event-details/event-details';
import { UserMessagingComponent } from './components/user-messaging/user-messaging';

export const routes: Routes = [
  // 1. Το σκέτο URL οδηγεί πλέον στη σελίδα καλωσορίσματος 
  { path: '', component: WelcomeComponent }, 

  // 2. Οι υπόλοιπες σελίδες της εφαρμογής 
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard', component: DashboardComponent }, 
  { path: 'search', component: EventSearchComponent }, 
  { path: 'event/:id', component: EventDetailsComponent },
  { path: 'messages', component: UserMessagingComponent },
  { path: '**', redirectTo: '' }
];