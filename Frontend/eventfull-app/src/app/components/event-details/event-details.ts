import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';

@Component({
  selector: 'app-event-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './event-details.html',
  styleUrl: './event-details.css'
})
export class EventDetailsComponent implements OnInit, OnDestroy {
  event: any = null;
  private map!: L.Map;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    const eventId = this.route.snapshot.paramMap.get('id');
    if (eventId) {
      this.fetchEventDetails(eventId);
    }
  }

  fetchEventDetails(id: string): void {
    // Παρακάμπτουμε προσωρινά το HTTP Get μέχρι ο συνεργάτης σου να προσθέσει τα event endpoints στο main.py.
    // Φορτώνουμε απευθείας τα δεδομένα για να δεις τη δουλειά σου ολοκληρωμένη!
    if (id === '2') {
      this.event = {
        EventID: '2',
        Title: 'AI Workshop 2026',
        Category: 'Tech',
        Venue: 'Συνεδριακό Κέντρο',
        City: 'Θεσσαλονίκη',
        StartDateTime: '2026-08-20T10:00:00',
        Price: 0,
        Description: 'Μάθετε τα πάντα για τα νέα παραγωγικά μοντέλα τεχνητής νοημοσύνης και τις εφαρμογές τους.',
        Latitude: '40.6293',
        Longitude: '22.9552'
      };
    } else {
      // Default για το ID 1 (Rock Summer Festival)
      this.event = {
        EventID: '1',
        Title: 'Rock Summer Festival',
        Category: 'Music',
        Venue: 'Τεχνόπολη',
        City: 'Αθήνα',
        StartDateTime: '2026-07-15T21:00:00',
        Price: 15,
        Description: 'Το μεγαλύτερο rock φεστιβάλ του καλοκαιριού στην Αθήνα με συμμετοχές κορυφαίων συγκροτημάτων!',
        Latitude: '37.9784',
        Longitude: '23.7142'
      };
    }

    // Αρχικοποίηση του χάρτη OpenStreetMap αμέσως μόλις μπουν τα δεδομένα
    setTimeout(() => {
      this.initMap();
    }, 50);
  }

  private initMap(): void {
    const lat = this.event?.Latitude ? parseFloat(this.event.Latitude) : 37.9784;
    const lng = this.event?.Longitude ? parseFloat(this.event.Longitude) : 23.7142;

    this.map = L.map('map').setView([lat, lng], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    const marker = L.marker([lat, lng]).addTo(this.map);
    
    if (this.event) {
      marker.bindPopup(`<b>${this.event.Title}</b><br>${this.event.Venue}`).openPopup();
    }

   
    setTimeout(() => {
      this.map.invalidateSize();
    }, 100);
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }
}