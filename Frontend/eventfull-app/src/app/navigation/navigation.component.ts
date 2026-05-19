import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, Router } from '@angular/router'; // Προσθέσαμε τον Router

@Component({
  selector: 'app-navigation',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navigation.html',  
  styleUrl: './navigation.css'
})
export class NavigationComponent {
  
  constructor(private router: Router) {} // Χρειαζόμαστε τον router για το logout

  // Χρησιμοποιούμε "getter" (get). Αυτό αναγκάζει την Angular 
  // να ελέγχει το localStorage αυτόματα, σε κάθε κλικ!
  get isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  logout() {
    localStorage.removeItem('access_token'); // Σβήνουμε το κλειδί
    this.router.navigate(['/']); // Σε πετάει στην Welcome σελίδα αμέσως
  }
}