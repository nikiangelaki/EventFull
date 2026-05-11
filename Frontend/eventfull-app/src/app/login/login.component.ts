import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { RouterLink, Router } from '@angular/router'; // Προστέθηκε το Router
import { AuthService } from '../auth'; // Βεβαιωθείτε ότι το path είναι σωστό

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
          alert('Επιτυχής σύνδεση!');
          localStorage.setItem('access_token', response.access_token);
        },
        error: (err) => {
          alert('Λάθος όνομα χρήστη ή κωδικός!');
          console.error(err);
        }
      });
    }
  }
}