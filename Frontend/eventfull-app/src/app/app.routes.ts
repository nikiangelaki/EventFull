import { Routes } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome.component';
import { LoginComponent } from './login/login.component';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { EventSearchComponent } from './components/event-search/event-search';
import { EventDetailsComponent } from './components/event-details/event-details';
import { UserMessagingComponent } from './components/user-messaging/user-messaging';
import { HomeComponent } from './home/home.component'; 
import { RegisterPendingComponent } from './components/register-pending/register-pending.component';
import { OrganizerDashboardComponent } from './components/organizer-dashboard/organizer-dashboard.component';
import { CreateEventComponent } from './components/create-event/create-event.component';

export const routes: Routes = [
  // 1. Το σκέτο URL οδηγεί στη σελίδα καλωσορίσματος (πριν το Login)
  { path: '', component: WelcomeComponent }, 

  // 2. Οι σελίδες σύνδεσης & εγγραφής
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'register-pending', component: RegisterPendingComponent },

  // 3. Η καθαρή Αρχική Σελίδα 
  { path: 'home', component: HomeComponent }, 

  // 4. Οι υπόλοιπες εσωτερικές σελίδες της εφαρμογής
  { path: 'dashboard', component: DashboardComponent }, // Η Διαχείρισή σου
  { path: 'search', component: EventSearchComponent }, // Η Αναζήτηση
  { path: 'event/:id', component: EventDetailsComponent },
  { path: 'messages', component: UserMessagingComponent },
  { path: 'organizer-dashboard', component: OrganizerDashboardComponent },
  { path: 'create-event', component: CreateEventComponent },
  //Αν κάποιος γράψει λάθος URL, γυρνάει στην αρχή
  { path: '**', redirectTo: '' }

 
];