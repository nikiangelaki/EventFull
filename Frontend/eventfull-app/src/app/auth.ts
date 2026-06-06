import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'https://127.0.0.1:8000'; 

  constructor(private http: HttpClient) { }

  // Διορθωμένη μέθοδος register που "περνάει" τα σφάλματα στο component
  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData).pipe(
      catchError((error) => {
        // Μεταφέρουμε το σφάλμα αυτούσιο στο component για να το διαχειριστούμε
        return throwError(() => error);
      })
    );
  }

  login(username: string, password: string): Observable<any> {
    const body = new HttpParams()
      .set('username', username) 
      .set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post(`${this.apiUrl}/login`, body.toString(), { headers: headers }).pipe(
      catchError((error) => {
        return throwError(() => error);
      })
    );
  }
 // Νέα μέθοδος για να παίρνουμε τα στοιχεία του συνδεδεμένου χρήστη
  getCurrentUser(): Observable<any> {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
    
    return this.http.get(`${this.apiUrl}/users/me`, { headers }).pipe(
      catchError((error) => {
        return throwError(() => error);
      })
    );
  }
}