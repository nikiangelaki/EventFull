import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';
import { AuthService } from '../auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  registerForm!: FormGroup;

  constructor(private authService: AuthService) {
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
      
      // 1. Παίρνουμε τις τιμές από τη φόρμα
      const formValues = this.registerForm.value;

      // 2. Φτιάχνουμε το "πακέτο" ακριβώς όπως το περιμένει το FastAPI (UserCreate)
      const payloadData = {
        username: formValues.username,
        email: formValues.email,
        password: formValues.password,
        role: formValues.role,
        first_name: formValues.name,       // Μετάφραση: name -> first_name
        last_name: formValues.lastname,    // Μετάφραση: lastname -> last_name
        phone: formValues.telephone,       // Μετάφραση: telephone -> phone
        address: formValues.address,
        afm: formValues.afm
        // Το confirmPassword το αγνοούμε εντελώς εδώ, δεν το στέλνουμε στο backend!
      };

      // 3. Στέλνουμε το σωστό πακέτο (payloadData) αντί για όλη τη φόρμα
      this.authService.register(payloadData).subscribe({
        next: (response) => {
          alert('Η εγγραφή ολοκληρώθηκε!');
          console.log(response);
        },
        error: (err) => {
          alert('Σφάλμα σύνδεσης με τον server');
          console.error(err);
        }
      });
    }
  }

}