import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserMessaging } from './user-messaging';

describe('UserMessaging', () => {
  let component: UserMessaging;
  let fixture: ComponentFixture<UserMessaging>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserMessaging],
    }).compileComponents();

    fixture = TestBed.createComponent(UserMessaging);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
