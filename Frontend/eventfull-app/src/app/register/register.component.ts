import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormControl, Validators, AbstractControl, ValidationErrors, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'; // Απαραίτητο για το *ngIf στο html
import { AuthService } from '../auth';
@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule], // Σιγουρέψου ότι υπάρχουν αυτά αν είναι standalone
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  registerForm!: FormGroup;
  errorMessage: string | null = null; // Προσθέτουμε τη μεταβλητή για το σφάλμα

  constructor(private authService: AuthService, private router: Router) {
    this.registerForm = new FormGroup({
      username: new FormControl('', [Validators.required]),
      password: new FormControl('', [Validators.required, Validators.minLength(8)]),
      confirmPassword: new FormControl('', [Validators.required]),
      name: new FormControl('', [Validators.required]),
      lastname: new FormControl('', [Validators.required]),
      email: new FormControl('', [Validators.required, Validators.email]),
      telephone: new FormControl('', [Validators.required, Validators.pattern('^[0-9]+$')]),
      address: new FormControl('', [Validators.required]),
      afm: new FormControl('', [Validators.required, Validators.minLength(9), Validators.maxLength(9), Validators.pattern('^[0-9]{9}$')]),
      role: new FormControl('organizer', [Validators.required])
    }, { validators: this.passwordMatchValidator }); 
  }

  passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password');
    const confirmPassword = control.get('confirmPassword');
    return password && confirmPassword && password.value !== confirmPassword.value 
      ? { passwordMismatch: true } 
      : null;
  }

  onSubmit() {
    if (this.registerForm.valid) {
      this.errorMessage = null; //Καθαρίζουμε παλιά σφάλματα πριν την προσπάθεια
      
      const formValues = this.registerForm.value;

      const payloadData = {
        username: formValues.username,
        email: formValues.email,
        password: formValues.password,
        role: formValues.role,
        first_name: formValues.name,       
        last_name: formValues.lastname,    
        phone: formValues.telephone,       
        address: formValues.address,
        afm: formValues.afm
      };

      this.authService.register(payloadData).subscribe({
        next: (response: any) => {
          console.log('Εγγραφή επιτυχής:', response);
          // Οδηγούμε τον χρήστη στη σελίδα αναμονής έγκρισης
          this.router.navigate(['/register-pending']);
        },
        error: (err: any) => {
          console.error(err);
          
          
          if (err.status === 400 || err.error?.detail?.includes('username') || err.error?.detail?.includes('already registered')) {
            this.errorMessage = 'Το όνομα χρήστη (Username) ή το Email χρησιμοποιείται ήδη. Παρακαλώ εισάγετε ένα καινούργιο.';
          } else {
            this.errorMessage = 'Παρουσιάστηκε σφάλμα σύνδεσης με τον server. Δοκιμάστε ξανά.';
          }
        }
      });
    }
  }
}