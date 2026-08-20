import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService, Page, Post, Token, User } from './api.service';
import { AppComponent } from './app.component';

const user: User = {id:2, username:'sam', is_moderator:false};
const post: Post = {id:1, author:{id:1,username:'alex',is_moderator:false}, title:'Welcome', body:'Hello', category:null, is_misleading:false, created_at:'2026-01-01T00:00:00Z', comments:[], like_count:0, comment_count:0, liked_by_me:false, ai_status:'failed', embedding_status:'failed', ai_moderation_score:null, ai_moderation_rationale:null, ai_needs_review:null};
const page = <T>(results:T[]):Page<T> => ({count:results.length,next:null,previous:null,results});

describe('AppComponent', () => {
  let component: AppComponent;
  let fixture: ComponentFixture<AppComponent>;
  let api: jasmine.SpyObj<ApiService>;

  beforeEach(async () => {
    api = jasmine.createSpyObj<ApiService>('ApiService', ['csrf','me','posts','categories','tokens','login','logout','createPost','comment','like','moderate','retryAi','createToken','revokeToken']);
    api.csrf.and.returnValue(of({})); api.me.and.returnValue(throwError(() => ({status:403})));
    api.posts.and.returnValue(of(page([post]))); api.categories.and.returnValue(of(page([]))); api.tokens.and.returnValue(of(page([])));
    await TestBed.configureTestingModule({imports:[AppComponent],providers:[{provide:ApiService,useValue:api}]}).compileComponents();
    fixture=TestBed.createComponent(AppComponent); component=fixture.componentInstance; fixture.detectChanges();
  });

  it('renders an anonymous feed even when there is no AI connection', () => {
    expect(component.posts).toEqual([post]);
    expect(fixture.nativeElement.textContent).toContain('Welcome');
    expect(fixture.nativeElement.textContent).toContain('Log in');
  });

  it('sets the authenticated user after login', () => {
    api.login.and.returnValue(of(user)); component.username='sam'; component.password='secret';
    component.login();
    expect(component.user).toEqual(user); expect(component.password).toBe(''); expect(api.posts).toHaveBeenCalled();
  });

  it('clears the composer after a successful post', () => {
    api.createPost.and.returnValue(of(post)); component.title='New idea'; component.body='Some context';
    component.create();
    expect(api.createPost).toHaveBeenCalledWith('New idea','Some context'); expect(component.title).toBe(''); expect(component.body).toBe('');
  });

  it('shows API failures without crashing the feed', () => {
    api.posts.and.returnValue(throwError(() => new HttpErrorResponse({status:503,error:{detail:'Semantic search is temporarily unavailable.'}})));
    component.load();
    expect(component.loading).toBeFalse(); expect(component.error).toContain('Semantic search');
  });

  it('shows a newly issued token only once in component state', () => {
    const token:Token={id:1,name:'CLI',prefix:'vf_123',created_at:'',revoked_at:null,token:'vf_secret'};
    api.createToken.and.returnValue(of(token)); component.tokenName='CLI'; component.createToken();
    expect(component.newToken).toBe('vf_secret'); expect(api.tokens).toHaveBeenCalled();
  });
});
