import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private apiUrl = 'https://127.0.0.1:8000/messages'; 

  constructor(private http: HttpClient) {}

  private getHeaders() {
    const token = localStorage.getItem('access_token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  // POST /messages/ -> Στείλε μήνυμα
 sendMessage(receiverId: any, content: string): Observable<any> {
    const payload = { 
      receiver_id: Number(receiverId), // Το μετατρέπουμε ΣΕ ΑΡΙΘΜΟ για να μην τρώμε 422!
      content: content,
      event_id: null // Το βάζουμε null αφού στο μοντέλο είναι nullable=True
    };
    
    console.log('Στέλνω αυτό το πακέτο στο FastAPI:', payload);
    return this.http.post(`${this.apiUrl}/`, payload, { headers: this.getHeaders() });
  }

  // GET /messages/inbox -> Πάρε τα εισερχόμενα
  getInbox(): Observable<any> {
    return this.http.get(`${this.apiUrl}/inbox`, { headers: this.getHeaders() });
  }

  // GET /messages/sent -> Πάρε τα απεσταλμένα
  getSentMessages(): Observable<any> {
    return this.http.get(`${this.apiUrl}/sent`, { headers: this.getHeaders() });
  }

  // GET /messages/{user_id} -> Άνοιξε τη συζήτηση
  getConversation(userId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/${userId}`, { headers: this.getHeaders() });
  }
}