import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withXsrfConfiguration } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ApiService, Post } from './api.service';

describe('ApiService', () => {
  let api: ApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({providers: [provideHttpClient(withXsrfConfiguration({cookieName:'csrftoken', headerName:'X-CSRFToken'})), provideHttpClientTesting()]});
    api = TestBed.inject(ApiService);
    http = TestBed.inject(HttpTestingController);
  });
  afterEach(() => http.verify());

  it('logs in with password credentials', () => {
    api.login('sam', 'secret').subscribe(user => expect(user.username).toBe('sam'));
    const request = http.expectOne('/api/v1/auth/login/');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({username:'sam', password:'secret'});
    expect(request.request.withCredentials).toBeTrue();
    request.flush({id:2, username:'sam', is_moderator:false});
  });

  it('encodes semantic-search input', () => {
    api.posts('', 'energy & cities').subscribe();
    const request = http.expectOne('/api/v1/posts/search/?q=energy%20%26%20cities');
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('filters the feed by category', () => {
    api.posts('technology').subscribe();
    const request = http.expectOne('/api/v1/posts/?category=technology');
    expect(request.request.method).toBe('GET');
    request.flush({count:0,next:null,previous:null,results:[]});
  });

  it('uses POST to like and DELETE to unlike', () => {
    api.like(7, false).subscribe();
    http.expectOne('/api/v1/posts/7/like/').flush({});
    api.like(7, true).subscribe();
    const unlike = http.expectOne('/api/v1/posts/7/like/');
    expect(unlike.request.method).toBe('DELETE');
    unlike.flush(null);
  });

  it('never calls an AI provider directly from the browser', () => {
    api.createPost('Title', 'Body').subscribe();
    const request = http.expectOne('/api/v1/posts/');
    expect(request.request.url).not.toContain('openai');
    request.flush({id:1} as Post);
  });
});

