import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RegisterPending } from './register-pending.component';

describe('RegisterPending', () => {
  let component: RegisterPending;
  let fixture: ComponentFixture<RegisterPending>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RegisterPending],
    }).compileComponents();

    fixture = TestBed.createComponent(RegisterPending);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
