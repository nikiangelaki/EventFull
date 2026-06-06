import { Component, OnInit } from '@angular/core';
import { EventService } from '../../services/event';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-organizer-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './organizer-dashboard.component.html',
  styleUrls: ['./organizer-dashboard.component.css']
})
export class OrganizerDashboardComponent implements OnInit {
  myEvents: any[] = [];

  constructor(private eventService: EventService) {}

  ngOnInit() {
    this.loadEvents();
  }

  loadEvents() {
    this.eventService.getOrganizerEvents().subscribe({
      next: (data) => {
        this.myEvents = data;
        console.log('Εκδηλώσεις που ήρθαν:', data); // Δες στην κονσόλα αν έρχονται δεδομένα
      },
      error: (err) => console.error('Σφάλμα φόρτωσης:', err)
    });
  }

  cancelEvent(eventId: string) {
  if (confirm('Είσαι σίγουρη ότι θέλεις να ακυρώσεις αυτή την εκδήλωση;')) {
    this.eventService.cancelEvent(eventId).subscribe({
      next: () => {
        alert('Η εκδήλωση ακυρώθηκε!');
        this.loadEvents(); // Ξαναφορτώνουμε τη λίστα για να φανούν οι αλλαγές
      },
      error: (err) => alert('Σφάλμα κατά την ακύρωση: ' + err.error.detail)
    });
  }
}
}