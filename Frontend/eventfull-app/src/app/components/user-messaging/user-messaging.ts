import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { MessageService } from '../../services/message';

@Component({
  selector: 'app-user-messaging',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-messaging.html',
  styleUrl: './user-messaging.css'
})
export class UserMessagingComponent implements OnInit {
  currentFolder: 'inbox' | 'sent' = 'inbox';
  
  // Εδώ θα αποθηκεύονται τα πραγματικά μηνύματα από τη βάση
  messages: any[] = []; 
  unreadCount: number = 0;

  constructor(private messageService: MessageService) {}

  ngOnInit() {
    this.loadMessages(); // Φόρτωσε τα μηνύματα μόλις ανοίξει η σελίδα
  }

  // Εναλλαγή καταλόγων (Inbox / Sent)
  switchFolder(folder: 'inbox' | 'sent'): void {
    this.currentFolder = folder;
    this.loadMessages(); // Κάθε φορά που αλλάζει φάκελος, τραβάμε τα σωστά δεδομένα
  }

  // Κεντρική συνάρτηση που φέρνει τα μηνύματα ανάλογα με τον φάκελο
  loadMessages() {
    if (this.currentFolder === 'inbox') {
      this.messageService.getInbox().subscribe({
        next: (data) => {
          this.messages = data;
          // Υπολογισμός unread αν το backend επιστρέφει πεδίο is_read ή isNew
          this.unreadCount = this.messages.filter(m => !m.is_read).length;
        },
        error: (err) => console.error('Σφάλμα inbox:', err)
      });
    } else {
      this.messageService.getSentMessages().subscribe({
        next: (data) => {
          this.messages = data;
        },
        error: (err) => console.error('Σφάλμα sent:', err)
      });
    }
  }

  // Επιστροφή των μηνυμάτων (πλέον επιστρέφει όλο το array αφού φιλτράρεται από το API)
  getActiveMessages() {
    return this.messages;
  }

  // Ανάγνωση Μηνύματος
  readMessage(msg: any): void {
    // Προσαρμογή στα ονόματα πεδίων που στέλνει το FastAPI (π.χ. sender_name, content, created_at)
    alert(`Ανάγνωση Μηνύματος:\n\nΠεριεχόμενο: ${msg.content}\nΗμερομηνία: ${msg.created_at || 'Άγνωστη'}`);
    
    // Εδώ αν ο φίλος σου έχει endpoint για "mark as read", μπορείς να το καλέσεις
    if (!msg.is_read) {
      msg.is_read = true;
      this.unreadCount = Math.max(0, this.unreadCount - 1);
    }
  }

  // Πραγματική Διαγραφή από τη Βάση Δεδομένων
  deleteMessage(id: number): void {
    if (confirm('Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το μήνυμα από τη βάση δεδομένων;')) {
      // Εδώ καλούμε το DELETE endpoint του φίλου σου (αν το έχεις προσθέσει στο service)
      // Για τώρα, κάνουμε μια προσομοίωση φιλτραρίσματος στην οθόνη:
      this.messages = this.messages.filter(m => m.id !== id);
      alert('Το μήνυμα αφαιρέθηκε!');
    }
  }

  openNewMessageModal(): void {
    // Εδώ μπορείς να βάλεις ένα prompt για γρήγορο τεστ αποστολής στη βάση!
    const receiverId = prompt('Δώσε το ID του Παραλήπτη:');
    const content = prompt('Γράψε το μήνυμα:');

    if (receiverId && content) {
      this.messageService.sendMessage(Number(receiverId), content).subscribe({
        next: (res) => {
          alert('Το μήνυμα στάλθηκε και γράφτηκε στη MySQL!');
          this.loadMessages(); // Ανανέωση λίστας
        },
        error: (err) => alert('Αποτυχία αποστολής στη βάση.')
      });
    }
  }
}