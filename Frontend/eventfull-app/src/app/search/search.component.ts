import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit {
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
  limit: number = 6; // 6 κάρτες ανά σελίδα (ταιριάζει τέλεια σε 3άδες grid)
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
    if (this.filters.maxPrice !== null) params = params.set('max_price', String(this.filters.maxPrice));

    this.http.get<any>(this.apiUrl, { params }).subscribe({
      next: (response) => {
        this.events = response.results || [];
        this.totalPages = response.total ? Math.ceil(response.total / this.limit) : 1;
      },
      error: (err) => {
        console.error('Σφάλμα κατά την αναζήτηση:', err);
      }
    });
  }

  changePage(newPage: number): void {
    if (newPage >= 1 && newPage <= this.totalPages) {
      this.page = newPage;
      this.searchEvents();
    }
  }

  viewDetails(eventId: string): void {
    this.router.navigate(['/event', eventId]);
  }
}