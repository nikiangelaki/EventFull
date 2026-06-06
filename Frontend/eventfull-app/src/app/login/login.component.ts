import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { RouterLink, Router } from '@angular/router'; 
import { AuthService } from '../auth'; 

@Component({
  selector: 'app-login',
  standalone: true, 
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
})
export class LoginComponent {
  loginForm = new FormGroup({
    username: new FormControl('', [Validators.required]), 
    password: new FormControl('', [Validators.required, Validators.minLength(8)])
  });

  constructor(private authService: AuthService, private router: Router) {}

  onLogin() {
    if (this.loginForm.valid) {
      const username = this.loginForm.value.username!; 
      const password = this.loginForm.value.password!;

      this.authService.login(username, password).subscribe({
        next: (response: any) => {
          localStorage.setItem('access_token', response.access_token);
          
          // Μόλις συνδεθεί, τραβάμε τα στοιχεία του χρήστη για να δούμε τον ρόλο του
          this.authService.getCurrentUser().subscribe({
            next: (user: any) => {
              localStorage.setItem('role', user.role); // Αποθηκεύουμε τον ρόλο για μελλοντική χρήση
              
              // Τώρα η δρομολόγηση γίνεται βάσει ρόλου!
              if (user.role === 'admin') {
                this.router.navigate(['/dashboard']);
              } else if (user.role === 'organizer') {
                this.router.navigate(['/organizer-dashboard']);
              } else {
                this.router.navigate(['/home']);
              }
            },
            error: (err) => {
              alert('Σφάλμα κατά την ανάκτηση στοιχείων χρήστη.');
            }
          });
        },
        error: (err) => {
          alert('Λάθος όνομα χρήστη ή κωδικός!');
        }
      });
    }
  }
}