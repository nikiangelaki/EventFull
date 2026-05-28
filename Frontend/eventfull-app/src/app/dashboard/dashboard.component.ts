import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule, NgFor, NgIf } from '@angular/common'; // Πλήρη Imports!
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, NgFor, NgIf, RouterLink], // Πλήρη Imports!
  templateUrl: './dashboard.component.html',
  styles: []
})
export class DashboardComponent implements OnInit {
  users: any[] = [];
  selectedUser: any = null;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadUsers(); 
  }

  loadUsers() {
    const token = localStorage.getItem('access_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.get('https://127.0.0.1:8000/admin/users', { headers }).subscribe({
      next: (data: any) => { 
        this.users = data; 
        this.cdr.detectChanges(); // Αναγκάζουμε την Angular να σχεδιάσει τον πίνακα!
      },
      error: (err: any) => console.error('Σφάλμα φόρτωσης χρηστών', err)
    });
  }

  viewUserDetails(username: string) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.get(`https://127.0.0.1:8000/admin/users/${username}`, { headers }).subscribe({
      next: (data: any) => { 
        this.selectedUser = data; 
        this.cdr.detectChanges();
      },
      error: (err: any) => console.error('Σφάλμα στοιχείων χρήστη', err)
    });
  }

  approveUser(username: string) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    this.http.patch(`https://127.0.0.1:8000/admin/users/${username}/approve`, {}, { headers }).subscribe({
      next: () => {
        alert(`Ο χρήστης ${username} εγκρίθηκε επιτυχώς!`);
        this.loadUsers();
        if (this.selectedUser?.username === username) {
          this.selectedUser.is_approved = true;
        }
        this.cdr.detectChanges();
      },
      error: (err: any) => console.error('Σφάλμα έγκρισης', err)
    });
  }

  rejectUser(username: string) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Authorization': `Bearer ${token}` };

    if (confirm(`Θέλετε σίγουρα να απορρίψετε την αίτηση του χρήστη ${username};`)) {
      this.http.delete(`https://127.0.0.1:8000/admin/users/${username}`, { headers }).subscribe({
        next: () => {
          alert(`Η αίτηση απορρίφθηκε.`);
          this.selectedUser = null;
          this.loadUsers();
        },
        error: (err: any) => console.error('Σφάλμα απόρριψης', err)
      });
    }
  }
}