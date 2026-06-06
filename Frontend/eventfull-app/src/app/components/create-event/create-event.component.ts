import { Component, AfterViewInit } from '@angular/core';
import { EventService } from '../../services/event';
import { FormGroup, FormControl, Validators, ReactiveFormsModule, FormArray } from '@angular/forms';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';

@Component({
  selector: 'app-create-event',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './create-event.component.html',
  styleUrls: ['./create-event.component.css']
})
export class CreateEventComponent implements AfterViewInit {
  map: any;
  marker: any;

  eventForm = new FormGroup({
    title: new FormControl('', Validators.required),
    category: new FormControl(''),
    eventType: new FormControl(''),
    venue: new FormControl(''),
    address: new FormControl(''),
    city: new FormControl(''),
    country: new FormControl(''),
    latitude: new FormControl(0),
    longitude: new FormControl(0),
    startDateTime: new FormControl('', Validators.required),
    endDateTime: new FormControl('', Validators.required),
    capacity: new FormControl('', [Validators.required, Validators.min(0), Validators.pattern('^[0-9]*$')]),
    description: new FormControl(''),
    mediaUrls: new FormControl(''),
    tickets: new FormArray([])
  });

  constructor(private eventService: EventService) {}

  ngAfterViewInit() {
    this.map = L.map('map').setView([37.9838, 23.7275], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);
    this.map.on('click', (e: any) => {
      if (this.marker) this.map.removeLayer(this.marker);
      this.marker = L.marker(e.latlng).addTo(this.map);
      this.eventForm.patchValue({ latitude: e.latlng.lat, longitude: e.latlng.lng });
    });
  }

  get tickets() { return this.eventForm.get('tickets') as FormArray; }

  addTicket() {
    this.tickets.push(new FormGroup({
      name: new FormControl('', Validators.required),
      price: new FormControl('', [Validators.required, Validators.min(0), Validators.pattern('^[0-9]+(\\.[0-9]{1,2})?$')]),
      quantity: new FormControl('', [Validators.required, Validators.min(0), Validators.pattern('^[0-9]*$')])
    }));
  }

  onSubmit() {
    if (this.eventForm.valid) {
      this.eventService.createEvent(this.eventForm.value).subscribe({
        next: () => alert('Επιτυχία!'),
        error: (err) => alert('Σφάλμα: ' + (err.error?.detail || 'Κάτι πήγε στραβά'))
      });
    } else {
      alert('Ελέγξτε τα πεδία σας. Η χωρητικότητα και το πλήθος πρέπει να είναι ακέραιοι, η τιμή έως 2 δεκαδικά.');
    }
  }
}