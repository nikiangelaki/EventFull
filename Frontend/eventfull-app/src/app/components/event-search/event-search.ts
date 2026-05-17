import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-event-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './event-search.html',
  styleUrl: './event-search.css'
})
export class EventSearchComponent implements OnInit {
  
  filters: {
    searchTerm: string;
    category: string;
    location: string;
    startDate: string;
    endDate: string;
    maxPrice: number | null;
  } = {
    searchTerm: '',
    category: '',
    location: '',
    startDate: '',
    endDate: '',
    maxPrice: null
  };

  events: any[] = [];
  page: number = 1;
  limit: number = 6;
  totalPages: number = 1;

  private apiUrl = 'https://127.0.0.1:8000/api/events/search';

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit(): void {
    this.searchEvents();
  }

  searchEvents(): void {
    let params = new HttpParams()
      .set('page', this.page.toString())
      .set('limit', this.limit.toString());

    if (this.filters.searchTerm) params = params.set('search', this.filters.searchTerm);
    if (this.filters.category) params = params.set('category', this.filters.category);
    if (this.filters.location) params = params.set('location', this.filters.location);
    if (this.filters.startDate) params = params.set('start_date', this.filters.startDate);
    if (this.filters.endDate) params = params.set('end_date', this.filters.endDate);
    
    if (this.filters.maxPrice !== null) {
      params = params.set('max_price', String(this.filters.maxPrice));
    }

    this.http.get<any>(this.apiUrl, { params }).subscribe({
      next: (response) => {
        this.events = response.results || [];
        this.totalPages = response.total ? Math.ceil(response.total / this.limit) : 1;
      },
      error: (err) => {
        console.error('Σφάλμα κατά την αναζήτηση, φορτώνονται δοκιμαστικά δεδομένα:', err);
        
        // Καταχωρούμε 2 δοκιμαστικές εκδηλώσεις για να δουλέψουμε αυτόνομα
        this.events = [
          {
            EventID: '1',
            Title: 'Rock Summer Festival',
            Category: 'Music',
            EventType: 'Μουσική',
            Venue: 'Τεχνόπολη',
            City: 'Αθήνα',
            StartDateTime: '2026-07-15T21:00:00',
            Price: 15,
            Description: 'Το μεγαλύτερο rock φεστιβάλ του καλοκαιριού στην Αθήνα!',
            Latitude: '37.9784',
            Longitude: '23.7142'
          },
          {
            EventID: '2',
            Title: 'AI Workshop 2026',
            Category: 'Tech',
            EventType: 'Τεχνολογία',
            Venue: 'Συνεδριακό Κέντρο',
            City: 'Θεσσαλονίκη',
            StartDateTime: '2026-08-20T10:00:00',
            Price: 0,
            Description: 'Μάθετε τα πάντα για τα νέα παραγωγικά μοντέλα τεχνητής νοημοσύνης.',
            Latitude: '40.6293',
            Longitude: '22.9552'
          }
        ];
        this.totalPages = 1;
      }
    });
  }

  validatePrice(event: any): void {
    const input = event.target;
    let cleanedValue = input.value.replace(/[^0-9]/g, '');
    this.filters.maxPrice = cleanedValue ? parseInt(cleanedValue, 10) : null;
    input.value = cleanedValue;
  }

  changePage(newPage: number): void {
    if (newPage >= 1 && newPage <= this.totalPages) {
      this.page = newPage;
      this.searchEvents();
    }
  }

  viewDetails(eventId: string): void {
    // ΣΟΣ: Η διαδρομή πρέπει να ταιριάζει με το router link
    this.router.navigate(['/event', eventId]);
  }
}