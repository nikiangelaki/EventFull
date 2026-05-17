import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-user-messaging',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './user-messaging.html',
  styleUrl: './user-messaging.css'
})
export class UserMessagingComponent {
  // Τρέχων κατάλογος: 'inbox' (Εισερχόμενα) ή 'sent' (Απεσταλμένα)
  currentFolder: 'inbox' | 'sent' = 'inbox';

  // Δοκιμαστικά δεδομένα (Mock Data) βασισμένα απόλυτα στην Απαίτηση 10
  messages = [
    { id: 1, folder: 'inbox', user: 'Γιάννης Π. (Διοργανωτής)', subject: 'Ερώτηση σχετικά με τη χωρητικότητα της εκδήλωσης', date: '27/03/2026', isNew: true },
    { id: 2, folder: 'inbox', user: 'Μαρία Κ.', subject: 'Αλλαγή θέσης στο Rock Summer Festival', date: '26/03/2026', isNew: false },
    { id: 3, folder: 'inbox', user: 'Σύστημα Εφαρμογής', subject: 'Η κράτησή σας επιβεβαιώθηκε επιτυχώς', date: '25/03/2026', isNew: false },
    { id: 4, folder: 'sent', user: 'Κώστας Μ. (Διοργανωτής)', subject: 'Επιβεβαίωση διαθεσιμότητας εισιτηρίων', date: '24/03/2026', isNew: false }
  ];

  // Εναλλαγή καταλόγων (Inbox / Sent)
  switchFolder(folder: 'inbox' | 'sent'): void {
    this.currentFolder = folder;
  }

  // Επιστροφή των μηνυμάτων του τρέχοντος καταλόγου
  getActiveMessages() {
    return this.messages.filter(m => m.folder === this.currentFolder);
  }

  // Προσομοίωση Ανάγνωσης Μηνύματος
  readMessage(msg: any): void {
    alert(`Ανάγνωση Μηνύματος:\n\nΑπό/Προς: ${msg.user}\nΘέμα: ${msg.subject}\nΗμερομηνία: ${msg.date}`);
    if (msg.isNew) {
      msg.isNew = false; // Μόλις διαβαστεί, αφαιρείται η ένδειξη "Νέο"
    }
  }

  // Μηχανισμός Διαγραφής Μηνύματος (Απαίτηση 10)
  deleteMessage(id: number): void {
    if (confirm('Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το μήνυμα από τον κατάλογο;')) {
      this.messages = this.messages.filter(m => m.id !== id);
    }
  }

  openNewMessageModal(): void {
    alert('Ανοίγει η φόρμα σύνταξης νέου μηνύματος προς τον Διοργανωτή/Συμμετέχοντα!');
  }
}