import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  //URL zoubou 'https://127.0.0.1:8000'; 
  private apiUrl = 'https://127.0.0.1:8000'; 

  constructor(private http: HttpClient) { }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, userData);
  }

  login(username: string, password: string): Observable<any> {
    const body = new HttpParams()
      .set('username', username) 
      .set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post(`${this.apiUrl}/login`, body.toString(), { headers: headers });
  }
}