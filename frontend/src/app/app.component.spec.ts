import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpErrorResponse } from '@angular/common/http';
import { of, throwError } from 'rxjs';
import { ApiService, Page, Post } from './api.service';
import { AppComponent } from './app.component';
const page=<T>(results:T[]):Page<T>=>({count:results.length,next:null,previous:null,results});
describe('AppComponent',()=>{let fixture:ComponentFixture<AppComponent>;beforeEach(async()=>{const api=jasmine.createSpyObj<ApiService>('ApiService',['csrf','me','posts','categories','tokens']);api.csrf.and.returnValue(of({}));api.me.and.returnValue(throwError(()=>new HttpErrorResponse({status:403})));api.posts.and.returnValue(of(page([] as Post[])));api.categories.and.returnValue(of(page([])));api.tokens.and.returnValue(of(page([])));await TestBed.configureTestingModule({imports:[AppComponent],providers:[{provide:ApiService,useValue:api}]}).compileComponents();fixture=TestBed.createComponent(AppComponent);fixture.detectChanges();});it('renders the production shell and anonymous empty state',()=>{expect(fixture.nativeElement.textContent).toContain('Verity');expect(fixture.nativeElement.textContent).toContain('No conversations found.');});});
