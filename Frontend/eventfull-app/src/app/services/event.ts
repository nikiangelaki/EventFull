import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class EventService {
  private apiUrl = 'https://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  private getHeaders() {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  createEvent(eventData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/events`, eventData, { headers: this.getHeaders() });
  }

  getOrganizerEvents(): Observable<any> {
    return this.http.get(`${this.apiUrl}/organizer/events`, { headers: this.getHeaders() });
  }

  cancelEvent(eventId: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/events/${eventId}/cancel`, {}, { headers: this.getHeaders() });
  }
}