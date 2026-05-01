import { Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { SearchComponent } from './search/search.component';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'search', component: SearchComponent }, 
  // 2. Πρόσθεσε αυτές τις δύο διαδρομές
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent }
];